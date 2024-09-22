#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Date::Calc qw(:all);
use Time::Local;
use REST::Client;

my $cgi = CGI->new;
my $SID;
my $method;

if (defined(cookie('SID'))) {
        $SID=cookie('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='cookies';
        }
elsif (defined(param('SID'))) {
        $SID=param('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='path';
        }
else {
        print "Location: http://localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $us_id=$sess->param('USER_ID');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

#Передача полей формы в скрипт зависит от поля "Посчитать занятия". Каждый способ расчета занятий требует определнных полей, а киких-то не требует. Таким образом в условии будет проверяться способ расчета и исходя из этого будем формировать массив передаваемых с формы полей 
#В самом начале проверяем на заполнение поля "Посчитать занятия", т.к. оно явдяется отправной точкой.

my $type_calc_lesson=param('TYPE_CALC_LESSON');
my $group_name=param('GROUP_NAME');
$type_calc_lesson=~s/\0//g; $type_calc_lesson=~s/\.\.//g; $type_calc_lesson=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$group_name=~s/\0//g; $group_name=~s/\.\.//g; $group_name=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
Encode::from_to($group_name,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно

########Проверка на ввод Посчитать занятия
if (length($type_calc_lesson)==0)
{
  my $ans="Необходимо заполнить \"Посчитать занятия\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных способов расчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($type_calc_lesson);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Способ расчета необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#################################Проверяем есть ли наименование вводимой группы уже в базе. Если есть, то ввод не возможен, т.к. групп с одинаковыми названиями не может быть!
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select GROUP_NAME from `groups` where `GROUP_NAME`=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($group_name);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt!=0)
{
  my $ans="Группа с наименованием \"".$group_name."\" уже существует в базе. Дублирование наименований недопустимо!";  
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################################################################################################


#Начинаем условием проверять какой способ расчета выбран и в зависимости от этого производим вставку данных в таблицу
###########################Если способ оплаты "По кол-ву часов", он имеет ID 1#####################################
if ($type_calc_lesson==1)
{
  #Создаем массив полей переданных из формы
  my @form_fields=(param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('KIND_PROGRAMM'), param('GROUP_NAME'), param('GROUP_TYPE'), param('TYPE_CALC_LESSON'), param('COUNT_CLASSES'), param('DURATION_CLASSES'), param('START_DATE'), param('COURSE_PRICE'), param('MIN_COUNT_STUDENTS'), param('MAX_COUNT_STUDENTS'), param('TYPE_PAY'), param('BRANCH'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
      Encode::from_to($el,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  }


########Проверка на ввод Курс
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить \"Курс\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Курс
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_languages where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Курс необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

=head
########Проверка на ввод Уровень
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить \"Уровень\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################
=cut

########Проверка на ввод Только корректных Уровней
if (length($form_fields[1])>0)
{
  my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

  my $sql_br="select ID from level_knowledge where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[1]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="Уровень необходимо выбирать только из списка!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка на ввод Программы
if (length($form_fields[2])==0)
{
  my $ans="Необходимо заполнить \"Программа\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Программ
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_programm where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Программу необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Наименования группы
if (length($form_fields[3])==0)
{
  my $ans="Необходимо заполнить \"Наименование группы\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на длинну Наименования Группы
if (length($form_fields[3])>255)
{
  my $ans="Длинна поля \"Наименование группы\" не может быть более 255 символов!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Тип группы
if (length($form_fields[4])==0)
{
  my $ans="Необходимо заполнить \"Тип группы\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Типов группы
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_groups where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[4]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Тип группы необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Способа расчета
if (length($form_fields[5])==0)
{
  my $ans="Необходимо заполнить \"Посчитать занятия\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Способов рпасчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Посчитать занятия\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод КОл-во занятий
if (length($form_fields[6])==0)
{
  my $ans="Необходимо заполнить \"Кол-во занятий\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка КОл-во занятий на ввод только цифр
if ($form_fields[6]!~m/^\d+$/i)
{
  my $ans="В поле \"Кол-во занятий\" необходимо вводить только цифры!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод длительность занятий
if (length($form_fields[7])==0)
{
  my $ans="Необходимо заполнить \"Продолжительность занятий\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка Продолжительность занятий на ввод только цифр (целые значения, не дробные)
if ($form_fields[7]!~m/^\d+$/i)
{
  my $ans="В поле \"Продолжительность занятий\" необходимо вводить только цифры!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#Проверка корректности даты начала
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[8]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата начала не корректна. Формат должен быть, например, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# Разбираем дату на день месяц и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[8]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате начала не корректен месяц. Месяц не может быть больше 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[8]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате начала не разумно большой год.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[8]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате начала не корректно задано число! Число не может быть более 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########Проверка на ввод цены курса
if (length($form_fields[9])==0)
{
  my $ans="Необходимо заполнить \"Цена курса\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка цены курса. Здесь используем регулярку, которая допускает ввод дробных и целых чисел
if ($form_fields[9]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
{
    my $ans="В поле \"Цена курса\" необходимо вводить только цифры (целые либо дробные)!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
}
##############################################################

########Проверка Минамальное кол-во студентов на ввод только цифр (целые значения, не дробные)
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d+$/i)
  {
    my $ans="В поле \"Минимальное кол-во студентов\" необходимо вводить только цифры!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка Максимальное кол-во студентов на ввод только цифр (целые значения, не дробные)
if (length($form_fields[11])>0)
{
  if ($form_fields[11]!~m/^\d+$/i)
  {
    my $ans="В поле \"Максимальное кол-во студентов\" необходимо вводить только цифры!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка, чтобы в поле Минимальное кол-во студентов не ввели большее число чем в максимальное
if (length($form_fields[10])>0 && length($form_fields[11])>0)
{
  if ($form_fields[11]<$form_fields[10])
  {
    my $ans="В поле \"Максимальное кол-во студентов\" невозможно вводить значение меньше чем в поле \"Минимальное кол-во студентов\"!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  } 
}

########Проверка на ввод Вида расчета
if (length($form_fields[12])==0)
{
  my $ans="Необходимо заполнить \"Вид расчета\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Видов расчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_pay where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[12]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Вид расчета\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Филиала
if (length($form_fields[13])==0)
{
  my $ans="Необходимо заполнить \"Филиал\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Филиалов
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from branches where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[13]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Филиал\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

  #Вставляем группу
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into groups (LANGUAGE, LEVEL_KNOWLEDGE, KIND_PROGRAMM, GROUP_NAME, GROUP_TYPE, TYPE_CALC_LESSON, COUNT_CLASSES, DURATION_CLASSES, START_DATE, COURSE_PRICE, MIN_COUNT_STUDENTS, MAX_COUNT_STUDENTS, TYPE_PAY, BRANCH, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";  
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $form_fields[13], $us_id);
  
      
  $dbh1->disconnect;

  my $ans="Группа добавлена успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
  ############################################################
}
###################Конец способ оплаты "По кол-ву часов", он имеет ID 1########################################



###################Если способ оплаты "По кол-ву занятий", он имеет ID 2
if ($type_calc_lesson==2)
{
  #Создаем массив полей переданных из формы
  my @form_fields=(param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('KIND_PROGRAMM'), param('GROUP_NAME'), param('GROUP_TYPE'), param('TYPE_CALC_LESSON'), param('COUNT_CLASSES'), param('START_DATE'), param('COURSE_PRICE'), param('MIN_COUNT_STUDENTS'), param('MAX_COUNT_STUDENTS'), param('TYPE_PAY'), param('BRANCH'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
      Encode::from_to($el,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  }


########Проверка на ввод Курс
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить \"Курс\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Курс
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_languages where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Курс необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

=head
########Проверка на ввод Уровень
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить \"Уровень\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################
=cut

########Проверка на ввод Только корректных Уровней
if (length($form_fields[1])>0)
{
  my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

  my $sql_br="select ID from level_knowledge where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[1]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="Уровень необходимо выбирать только из списка!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка на ввод Программы
if (length($form_fields[2])==0)
{
  my $ans="Необходимо заполнить \"Программа\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Программ
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_programm where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Программу необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Наименования группы
if (length($form_fields[3])==0)
{
  my $ans="Необходимо заполнить \"Наименование группы\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на длинну Наименования Группы
if (length($form_fields[3])>255)
{
  my $ans="Длинна поля \"Наименование группы\" не может быть более 255 символов!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Тип группы
if (length($form_fields[4])==0)
{
  my $ans="Необходимо заполнить \"Тип группы\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Типов группы
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_groups where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[4]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Тип группы необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Способа расчета
if (length($form_fields[5])==0)
{
  my $ans="Необходимо заполнить \"Посчитать занятия\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Способов рпасчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Посчитать занятия\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод КОл-во занятий
if (length($form_fields[6])==0)
{
  my $ans="Необходимо заполнить \"Кол-во занятий\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка КОл-во занятий на ввод только цифр
if ($form_fields[6]!~m/^\d+$/i)
{
  my $ans="В поле \"Кол-во занятий\" необходимо вводить только цифры!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#Проверка корректности даты начала
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[7]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата начала не корректна. Формат должен быть, например, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# Разбираем дату на день месяц и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[7]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате начала не корректен месяц. Месяц не может быть больше 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[7]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате начала не разумно большой год.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[7]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате начала не корректно задано число! Число не может быть более 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########Проверка на ввод цены курса
if (length($form_fields[8])==0)
{
  my $ans="Необходимо заполнить \"Цена курса\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка цены курса. Здесь используем регулярку, которая допускает ввод дробных и целых чисел
if ($form_fields[8]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
{
    my $ans="В поле \"Цена курса\" необходимо вводить только цифры (целые либо дробные)!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
}
##############################################################

########Проверка Минамальное кол-во студентов на ввод только цифр (целые значения, не дробные)
if (length($form_fields[9])>0)
{
  if ($form_fields[9]!~m/^\d+$/i)
  {
    my $ans="В поле \"Минимальное кол-во студентов\" необходимо вводить только цифры!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка Максимальное кол-во студентов на ввод только цифр (целые значения, не дробные)
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d+$/i)
  {
    my $ans="В поле \"Максимальное кол-во студентов\" необходимо вводить только цифры!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка, чтобы в поле Минимальное кол-во студентов не ввели большее число чем в максимальное
if (length($form_fields[9])>0 && length($form_fields[10])>0)
{
  if ($form_fields[10]<$form_fields[9])
  {
    my $ans="В поле \"Максимальное кол-во студентов\" невозможно вводить значение меньше чем в поле \"Минимальное кол-во студентов\"!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  } 
}

########Проверка на ввод Вида расчета
if (length($form_fields[11])==0)
{
  my $ans="Необходимо заполнить \"Вид расчета\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Видов расчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_pay where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[11]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Вид расчета\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Филиала
if (length($form_fields[12])==0)
{
  my $ans="Необходимо заполнить \"Филиал\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Филиалов
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from branches where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[12]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Филиал\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################


  #Вставляем группу
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into groups (LANGUAGE, LEVEL_KNOWLEDGE, KIND_PROGRAMM, GROUP_NAME, GROUP_TYPE, TYPE_CALC_LESSON, COUNT_CLASSES, START_DATE, COURSE_PRICE, MIN_COUNT_STUDENTS, MAX_COUNT_STUDENTS, TYPE_PAY, BRANCH, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";  
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $us_id);
        
  $dbh1->disconnect;

  my $ans="Группа добавлена успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
  ############################################################
}
###################Конец способ оплаты "По кол-ву занятий", он имеет ID 2########################################




###################Если способ оплаты "По дате окончания", он имеет ID 3
if ($type_calc_lesson==3)
{
  #Создаем массив полей переданных из формы
  my @form_fields=(param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('KIND_PROGRAMM'), param('GROUP_NAME'), param('GROUP_TYPE'), param('TYPE_CALC_LESSON'), param('START_DATE'), param('END_DATE'), param('COURSE_PRICE'), param('MIN_COUNT_STUDENTS'), param('MAX_COUNT_STUDENTS'), param('TYPE_PAY'), param('BRANCH'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
      Encode::from_to($el,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  }


########Проверка на ввод Курс
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить \"Курс\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Курс
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_languages where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Курс необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

=head
########Проверка на ввод Уровень
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить \"Уровень\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################
=cut

########Проверка на ввод Только корректных Уровней
if (length($form_fields[1])>0)
{
  my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

  my $sql_br="select ID from level_knowledge where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[1]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="Уровень необходимо выбирать только из списка!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка на ввод Программы
if (length($form_fields[2])==0)
{
  my $ans="Необходимо заполнить \"Программа\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Программ
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_programm where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Программу необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Наименования группы
if (length($form_fields[3])==0)
{
  my $ans="Необходимо заполнить \"Наименование группы\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на длинну Наименования Группы
if (length($form_fields[3])>255)
{
  my $ans="Длинна поля \"Наименование группы\" не может быть более 255 символов!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Тип группы
if (length($form_fields[4])==0)
{
  my $ans="Необходимо заполнить \"Тип группы\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Типов группы
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_groups where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[4]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Тип группы необходимо выбирать только из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Способа расчета
if (length($form_fields[5])==0)
{
  my $ans="Необходимо заполнить \"Посчитать занятия\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Способов расчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Посчитать занятия\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#Проверка корректности даты начала
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[6]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата начала не корректна. Формат должен быть, например, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# Разбираем дату на день месяц и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[6]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате начала не корректен месяц. Месяц не может быть больше 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[6]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате начала не разумно большой год.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[6]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате начала не корректно задано число! Число не может быть более 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

#Проверка корректности даты окончания
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[7]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата начала не корректна. Формат должен быть, например, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# Разбираем дату на день месяц и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[7]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате начала не корректен месяц. Месяц не может быть больше 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[7]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате начала не разумно большой год.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
$form_fields[7]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате начала не корректно задано число! Число не может быть более 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########Сравнение дат, чтобы пользователь случайно не ввел дату начала меньше даты окончания
my @f = ($form_fields[6] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my @e = ($form_fields[7] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
my $sepoch = timelocal(0,0,0,$e[2],$e[1]-1,$e[0]);
if ($fepoch>$sepoch)
{
  my $ans="Дата начала не может быть больше даты окончания";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
}
############################################################################################

########Проверка на ввод цены курса
if (length($form_fields[8])==0)
{
  my $ans="Необходимо заполнить \"Цена курса\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка цены курса. Здесь используем регулярку, которая допускает ввод дробных и целых чисел
if ($form_fields[8]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
{
    my $ans="В поле \"Цена курса\" необходимо вводить только цифры (целые либо дробные)!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
}
##############################################################

########Проверка Минамальное кол-во студентов на ввод только цифр (целые значения, не дробные)
if (length($form_fields[9])>0)
{
  if ($form_fields[9]!~m/^\d+$/i)
  {
    my $ans="В поле \"Минимальное кол-во студентов\" необходимо вводить только цифры!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка Максимальное кол-во студентов на ввод только цифр (целые значения, не дробные)
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d+$/i)
  {
    my $ans="В поле \"Максимальное кол-во студентов\" необходимо вводить только цифры!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########Проверка, чтобы в поле Минимальное кол-во студентов не ввели большее число чем в максимальное
if (length($form_fields[9])>0 && length($form_fields[10])>0)
{
  if ($form_fields[10]<$form_fields[9])
  {
    my $ans="В поле \"Максимальное кол-во студентов\" невозможно вводить значение меньше чем в поле \"Минимальное кол-во студентов\"!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  } 
}

########Проверка на ввод Вида расчета
if (length($form_fields[11])==0)
{
  my $ans="Необходимо заполнить \"Вид расчета\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Видов расчета
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_pay where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[11]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Вид расчета\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Филиала
if (length($form_fields[12])==0)
{
  my $ans="Необходимо заполнить \"Филиал\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Филиалов
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from branches where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[12]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Филиал\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################


  #Вставляем группу
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into `groups` (`LANGUAGE`, `LEVEL_KNOWLEDGE`, `KIND_PROGRAMM`, `GROUP_NAME`, `GROUP_TYPE`, `TYPE_CALC_LESSON`, `START_DATE`, `END_DATE`, `COURSE_PRICE`, `MIN_COUNT_STUDENTS`, `MAX_COUNT_STUDENTS`, `TYPE_PAY`, `BRANCH`, `USER_ID`, `DATETIME_CREATE`) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";  
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $us_id);
        
  $dbh1->disconnect;
  
  #######Используем модуль для работы с REST запросами для доступа к нашему облаку
  #Подключаемся к облаку и получаем SID, чтобы в дальнейшем с помощью него создавать папку группы
  my $client_rest = REST::Client->new();
  $client_rest->GET('http://46.180.119.231:5533/webapi/auth.cgi?api=SYNO.API.Auth&version=3&method=login&account=LinguaPlatform&passwd=Lingua2021!&session=FileStation&format=sid');
  my $res_json = JSON->new->utf8->decode($client_rest->responseContent());
  my $sid_cloud=$res_json->{'data'}->{'sid'};
  
  #Создаем папку на облаке
  my $client_folder = REST::Client->new();
  $client_folder->GET('http://46.180.119.231:5533/webapi/entry.cgi?api=SYNO.FileStation.CreateFolder&version=2&method=create&folder_path=%5B%22%2FLinguaPlatform%22%5D&name=%5B%22'.$form_fields[3].'%22%5D&_sid='.$sid_cloud);
  $client_folder->responseContent();

  my $ans="Группа добавлена успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
  ############################################################
}
###################Конец способ оплаты "По дате окончания", он имеет ID 3########################################


#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
