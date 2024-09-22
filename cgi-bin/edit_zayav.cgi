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

#use Log::Any qw($log);
#use Log::Any::Adapter ('Stdout');
#use Log::Any::Adapter ('File', 'file.log');
#use Log::Any::For::Std;


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

my $idd=param('id_x');
my $uuid=param('uuid');
my $dt_br=param('DATE_OF_BORN');

$idd=~s/\0//g; $idd=~s/\.\.//g; $idd=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$uuid=~s/\0//g; $uuid=~s/\.\.//g; $uuid=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$dt_br=~s/\0//g; $dt_br=~s/\.\.//g; $dt_br=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my $dt;
if (length($dt_br)>0) { $dt=$dt_br; } else { $dt="0000"; }

#Создаем массив полей переданных из формы
my @form_fields=(param('WHO_GET_ZAYAV'), param('SOURCE_ZAYAV'), param('FIO_STUDENT'), param('FIO_PARENT'), $dt, param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('BRANCH'), param('PHONE'), param('SOURCE_ABOUT_US'), param('DATE_OF_TEST'), param('TIME_OF_TEST'), param('NOTES'));

for(my $n=0; $n<=$#form_fields; $n++ )
{
        $form_fields[$n]=~s/\0//g;
        $form_fields[$n]=~s/\.\.//g;
        $form_fields[$n]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        Encode::from_to($form_fields[$n],'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
}

########Проверка на ввод Заявку принял
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить \"Заявку принял\"!";
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

########Проверка на ввод Только корректных сотрудников кто принял заявку
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from users_get_zayav where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Сотрудника, кто принял заявку необходимо выбирать только из списка!";
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

########Проверка на ввод Источник заявки
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить \"Источник заявки\"!";
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

########Проверка на ввод Только корректных сотрудников кто принял заявку
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from source_zayav where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[1]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Сотрудника, кто принял заявку необходимо выбирать только из списка!";
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

########Проверка на ввод ФИО
if (length($form_fields[2])==0)
{
  my $ans="Необходимо заполнить \"ФИО\"!";
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

########Проверка на длинну ФИО
if (length($form_fields[2])>150)
{
  my $ans="Длинна\"ФИО\" не может быть более 150 символов!";
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

########Проверка на длинну ФИО родителя
if (length($form_fields[3])>150)
{
  my $ans="Длинна\"ФИО\" родителя не может быть более 150 символов!";
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
########Проверка на ввод ДР
if (length($form_fields[4])==0)
{
  my $ans="Необходимо заполнить \"Дату рождения\"!";
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

#Проверка корректности даты рождения
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[4]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата ДР не корректна. Формат должен быть, например, 2016-05-30.";
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
$form_fields[4]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате ДР не корректен месяц. Месяц не может быть больше 12!";
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
$form_fields[4]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате ДР не разумно большой год.";
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
$form_fields[4]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате ДР не корректно задано число! Число не может быть более 31!";
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
=cut

########Проверка на ввод Курса
if (length($form_fields[5])==0)
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

########Проверка на ввод Только корректных курсов
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from kind_languages where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Наименование курса необходимо выбирать только из списка!";
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

########Проверка на ввод Только корректных уровней владения языком
if (length($form_fields[6])>0)
{
  my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД  
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
  my $sql_br="select ID from level_knowledge where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[6]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="Уровень владения языком необходимо выбирать только из списка!";
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

########Проверка на ввод филиала
if (length($form_fields[7])==0)
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

########Проверка на ввод Только корректных филиалов
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from branches where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[7]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Филиал необходимо выбирать только из списка!";
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

########Проверка на ввод откуда о нас узнали
if (length($form_fields[9])==0)
{
  my $ans="Необходимо заполнить \"Откуда о нас узнали\"!";
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

########Проверка на ввод Только корректных откуда о нас узнали
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from source_about_us where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[9]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="\"Откуда о нас узнали\" необходимо выбирать только из списка!";
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

#Проверка корректности даты тестирования
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
  {
        my $ans="Введенная дата тестирования не корректна. Формат должен быть, например, 2016-05-30.";
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
  $form_fields[10]=~/(?<=-)(\d{2})(?=-)/;
  if ($&>12)
  {
        my $ans="В введенной дате тестирования не корректен месяц. Месяц не может быть больше 12!";
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
  $form_fields[10]=~/\d{4}/;
  if ($&>3000)
  {
        my $ans="В введенной дате тестирования не разумно большой год.";
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
  $form_fields[10]=~/(?<=-)(\d{2})$/;
  if ($&>31)
  {
        my $ans="В введенной дате тестирования не корректно задано число! Число не может быть более 31!";
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
  ############################################################################################################################################


my $result_age;

if (length($dt_br)>0)
{  
  #Извлекаем текущую дату
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
  $year=$year+1900;
  $mon=$mon+1;
  my $today_date=$year."-".$mon."-".$mday; #Формируем дату в нужном формате

  #Разбиваем ДР студента полученную с формы на год, месяц и день

  $form_fields[4]=~/(?<=-)(\d{2})(?=-)/;
  my $us_m=$&;
        
  # Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
  $form_fields[4]=~/\d{4}/;
  my $us_y=$&;
        
  # Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
  $form_fields[4]=~/(?<=-)(\d{2})$/;
  my $us_d=$&;

  ################Подсчет разницы между датами в формате год, месяц день
  my ($Dy,$Dm,$Dd) = N_Delta_YMD($us_y,$us_m,$us_d,$year,$mon,$mday);
  
  if ($Dy<7)
  {
    $result_age=$Dy." лет ".$Dm." мес.";
  }
  else
  {
    $result_age=$Dy." лет";
  }  
  #my $result_age=$Dy." лет ".$Dm." мес.";
  #############################################
  } else { $result_age="0 лет"; }

  if ($form_fields[4] ne "0000")
  {
    my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth1=$dbh1->do("SET NAMES 'cp1251'");
    my $sql1="update zayavki set WHO_GET_ZAYAV=?, SOURCE_ZAYAV=?, FIO_STUDENT=?, FIO_PARENT=?, DATE_OF_BORN=?, LANGUAGE=?, LEVEL_KNOWLEDGE=?, BRANCH=?, PHONE=?, SOURCE_ABOUT_US=?, DATE_OF_TEST=?, TIME_OF_TEST=?, NOTES=?, AGE_STUDENT=? where ID=?";
    $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
    $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $result_age, $idd);
    $dbh1->disconnect;
  }
   else
  {
    my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth2=$dbh2->do("SET NAMES 'cp1251'");
    my $sql2="update zayavki set WHO_GET_ZAYAV=?, SOURCE_ZAYAV=?, FIO_STUDENT=?, FIO_PARENT=?, DATE_OF_BORN=null, LANGUAGE=?, LEVEL_KNOWLEDGE=?, BRANCH=?, PHONE=?, SOURCE_ABOUT_US=?, DATE_OF_TEST=?, TIME_OF_TEST=?, NOTES=?, AGE_STUDENT=? where ID=?";
    $sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
    $sth2->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $result_age, $idd);
    $dbh2->disconnect;
  }
  
 #Редактируем событие в календаре на основании произведенных изменений в заявке
  my $com_datetime=$form_fields[10]." ".$form_fields[11];
  my $txt_message="Тестирование студента: ".$form_fields[2];
  #my $lang="Язык:".$form_fields[5];
  
  my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  my $sql="update calendar_events set START_DATE=?, END_DATE=?, TEXT_MESSAGE=?, DETAILS=(select CONCAT ('Язык: ', LANGUAGE) from kind_languages where ID=?), USER_ID_UPDATE_EVENT=? where UUID_IND_ZAYAV=?";
  $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
  $sth->execute($com_datetime, $com_datetime, $txt_message, $form_fields[5], $us_id, $uuid);
  $dbh->disconnect;

  my $ans="Заявка отредактирована успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################



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
