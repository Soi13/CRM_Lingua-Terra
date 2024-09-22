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

  #Создаем массив полей переданных из формы
  my @form_fields=(param('TYPE_DOC'), param('COURSE'), param('TYPE_GROUP'), param('PRICE_COURSE'), param('DATE_START_DOGOVOR'), param('DATE_END_DOGOVOR'), param('TEXT_DOCUM'), param('num_dog_stud'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;      
  }


########Проверка на ввод Тип документа
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить \"Тип документа\"!";
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

########Проверка на ввод Только корректных типов документа
my $dbh_tp=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_tp=$dbh_tp->do("SET NAMES 'cp1251'");

my $sql_tp="select ID from type_doc where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_tp=$dbh_tp->prepare($sql_tp);
$sth_tp->execute($form_fields[0]);
my $cnt=$sth_tp->rows();
$dbh_tp->disconnect();

if ($cnt==0)
{
  my $ans="Тип документа необходимо выбирать только из списка!";
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

########Проверка на ввод Курса
if (length($form_fields[1])==0)
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

########Проверка на ввод Только корректных Курсов
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from kind_programm where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[1]);
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

########Проверка на ввод типа группы
if (length($form_fields[2])==0)
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

########Проверка на ввод Только корректных типов групп
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from type_groups where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
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

########Проверка на цены курса
if (length($form_fields[3])==0)
{
  my $ans="Необходимо заполнить \"Цену курса\"!";
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
if ($form_fields[3]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
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

#Проверка корректности даты начала договора
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[4]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата начала договора не корректна. Формат должен быть, например, 2016-05-30.";
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
        my $ans="В введенной дате начала договора не корректен месяц. Месяц не может быть больше 12!";
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
        my $ans="В введенной дате начала договора не разумно большой год.";
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
        my $ans="В введенной дате начала договора не корректно задано число! Число не может быть более 31!";
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

#Проверка корректности даты окончания договора
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[5]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата окончания договора не корректна. Формат должен быть, например, 2016-05-30.";
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
$form_fields[5]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате окончания договора не корректен месяц. Месяц не может быть больше 12!";
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
$form_fields[5]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате окончания договора не разумно большой год.";
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
$form_fields[5]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате окончания договора не корректно задано число! Число не может быть более 31!";
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
my @f = ($form_fields[4] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my @e = ($form_fields[5] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
my $sepoch = timelocal(0,0,0,$e[2],$e[1]-1,$e[0]);
if ($fepoch>$sepoch)
{
  my $ans="Дата начала договора не может быть больше даты окончания";
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

########Проверка на ввод шаблона
if (length($form_fields[6])==0)
{
  my $ans="Необходимо заполнить \"Шаблон\"!";
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

########Проверка на ввод Только корректных типов документа
my $dbh_tp=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_tp=$dbh_tp->do("SET NAMES 'cp1251'");

my $sql_tp="select ID from document_templates where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_tp=$dbh_tp->prepare($sql_tp);
$sth_tp->execute($form_fields[6]);
my $cnt=$sth_tp->rows();
$dbh_tp->disconnect();

if ($cnt==0)
{
  my $ans="Шаблон необходимо выбирать только из списка!";
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


  #Получаем всю инфу (все поля) о студенте к которому привязываем документ
  my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  my $sql="select * from pupils where Num_dogovor=?";
  $sth=$dbh->prepare($sql);
  $sth->execute($form_fields[7]);
  #В массив записываем извлеченную строку
  my @row_student = $sth->fetchrow_array;
  $dbh->disconnect;

  #Получаем текст шаблона документа на основании которого будем формировать документ
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select TEXT_OF_DOCUMENT from document_templates where ID=?";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute($form_fields[6]);
  #В массив записываем извлеченную строку
  my @row_template = $sth1->fetchrow_array;
  $dbh1->disconnect;
  
  #Получаем всю инфу по типу группы
  my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="select * from type_groups where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2]);
  #В массив записываем извлеченную строку
  my @row_type_group = $sth2->fetchrow_array;
  $dbh2->disconnect;
  
  #Получаем имя курса
  my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="select NAME_PROGRAMM from kind_programm where ID=?";
  $sth3=$dbh3->prepare($sql3);
  $sth3->execute($form_fields[1]);
  #В массив записываем извлеченную строку
  my @row_course = $sth3->fetchrow_array;
  $dbh3->disconnect;
  
  
  my $res_price=$row_type_group[1]." - ".$row_type_group[2]."./".$row_type_group[3].". Длительность: ".$row_type_group[5]; #Формируем общую строку стоимости для помещения в договор
   
  $row_template[0]=~s/%НОМЕР_ДОГОВОРА%/$row_student[0]/ig;  
  $row_template[0]=~s/%ДАТА_НАЧАЛА_ДОГОВОРА%/$form_fields[4]/ig;  
  $row_template[0]=~s/%ФИО_СТУДЕНТА%/$row_student[1]/ig;
  $row_template[0]=~s/%ВИД_ПРОГРАММЫ%/$row_course[0]/ig;
  $row_template[0]=~s/%ПОЛНАЯ_СТОИМОСТЬ_КУРСА%/$form_fields[3]/ig;
  $row_template[0]=~s/%ДАТА_ОКОНЧАНИЯ_ДОГОВОРА%/$form_fields[5]/ig;
  $row_template[0]=~s/%СЕРИЯ_ПАСПОРТА_СТУДЕНТА%/$row_student[10]/ig;
  $row_template[0]=~s/%НОМЕР_ПАСПОРТА_СТУДЕНТА%/$row_student[18]/ig;
  $row_template[0]=~s/%КЕМ_ВЫДАН_ПАСПОРТ_СТУДЕНТА%/$row_student[19]/ig;
  $row_template[0]=~s/%КОГДА_ВЫДАН_ПАСПОРТ_СТУДЕНТА%/$row_student[20]/ig;
  $row_template[0]=~s/%ДОМ_АДРЕС%/$row_student[5]/ig;
  $row_template[0]=~s/%МОБ_ТЕЛЕФОН%/$row_student[6]/ig;  
  $row_template[0]=~s/%СТОИМОСТЬ ОБУЧЕНИЯ%/$res_price/ig;  
  $row_template[0]=~s/%ФИО_РОДИТЕЛЯ_СТУДЕНТА%/$row_student[13]/ig;  
  $row_template[0]=~s/%ДАТА_РОЖДЕНИЯ_СТУДЕНТА%/$row_student[2]/ig;  
  $row_template[0]=~s/%СЕРИЯ_ПАСПОРТА_РОДИТЕЛЯ%/$row_student[15]/ig;  
  $row_template[0]=~s/%НОМЕР_ПАСПОРТА_РОДИТЕЛЯ%/$row_student[14]/ig;  
  $row_template[0]=~s/%КЕМ_ВЫДАН_ПАСПОРТ_РОДИТЕЛЯ%/$row_student[16]/ig;  
  $row_template[0]=~s/%КОГДА_ВЫДАН_ПАСПОРТ_РОДИТЕЛЯ%/$row_student[17]/ig;  
  
  
  #Вставляем запись о привязке
  my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="insert into document_students (PUPILS_Num_dogovor, TYPE_DOC, COURSE, TYPE_GROUP, PRICE_COURSE, DATE_START_DOGOVOR, DATE_END_DOGOVOR, TEXT_DOCUM, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?, NOW())";  
  $sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
  $sth2->execute($form_fields[7], $form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $row_template[0], $us_id);    
  $dbh2->disconnect;

  #Обновляем студента и добавляем ему программу/курс, указанный в договоре. Это для возможности фильтрации по студентам по виду программы при создании группы.
  my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="update pupils set KIND_PROG_FROM_DOGOVOR=? where Num_dogovor=?";  
  $sth3=$dbh3->prepare($sql3); #Для операций которые не возвращают значение
  $sth3->execute($form_fields[1], $row_student[0]);
  $dbh3->disconnect;
  
  my $ans="Документ привязан успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
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
