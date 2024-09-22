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


my $cgi = CGI->new;
my $SID;
my $method;

if (defined(cookie('SID'))) {
        $SID=cookie('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g;  $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='cookies';
        }
elsif (defined(param('SID'))) {
        $SID=param('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g;  $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
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

my $FIO_STUDENT=param('FIO');
my $DATE_OF_BORN=param('DATE_OF_BORN');
my $PLACE_WORK_STUDY=param('PLACE_OF_WORK');
my $POSITION_FACULTET=param('POSITION_FACULT');
my $HOME_ADDR=param('HOME_ADDRESS');
my $MOBILE_PHONE=param('MOBILE_PHONE');
my $HOME_PHONE=param('HOME_PHONE');
my $WORK_PHONE=param('WORK_PHONE');
my $EM=param('EMAIL');
my $SER_PASSPORT=param('PASSPORT');
my $SOURCE_ABOUT_US=param('SOURCE_ABOUT_US');
my $DATE_OF_FILLING=param('DATE_OF_FILLING');
my $FIO_PARENT=param('FIO_PARENT');
my $NUM_PASSPORT_PARENT=param('NUM_PASSPORT_PARENT');
my $SER_PASSPORT_PARENT=param('SER_PASSPORT_PARENT');
my $KEM_VIDAN_PASSPORT_PARENT=param('KEM_VIDANO_PASSPORT_PARENT');
my $KOGDA_VIDAN_PASSPORT_PARENT=param('KOGDA_VIDANO_PASSPORT_PARENT');
my $NUM_PASSPORT=param('PASSPORT_NUM');
my $KEM_VIDAN_PASSPORT=param('PASSPORT_VIDAN');
my $KOGDA_VIDAN_PASSPORT=param('PASSPORT_DATE');
my $SEX=param('SEX');
my $BRANCH=param('BRANCH');
my $MOBILE_PHONE_CHILD=param('MOBILE_CHILD');
my $STUDENT_INTERESTS=param('STUDENT_INTERESTS');
my $AGREE_GET_SMS=param('AGREMMENT_GET_SMS');
my $AGREE_GET_EMAIL=param('AGREMMENT_GET_EMAIL');
my $AGREE_USE_PHOTO=param('AGREMMENT_USE_PHOTO');
my $BARTER=param('BARTER');
my $INDIVIDUAL=param('INDIVIDUAL');

$FIO_STUDENT=~s/\0//g; $FIO_STUDENT=~s/\.\.//g; $FIO_STUDENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DATE_OF_BORN=~s/\0//g; $DATE_OF_BORN=~s/\.\.//g; $DATE_OF_BORN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PLACE_WORK_STUDY=~s/\0//g; $PLACE_WORK_STUDY=~s/\.\.//g; $PLACE_WORK_STUDY=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$POSITION_FACULTET=~s/\0//g; $POSITION_FACULTET=~s/\.\.//g; $POSITION_FACULTET=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$HOME_ADDR=~s/\0//g; $HOME_ADDR=~s/\.\.//g; $HOME_ADDR=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$MOBILE_PHONE=~s/\0//g; $MOBILE_PHONE=~s/\.\.//g; $MOBILE_PHONE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$HOME_PHONE=~s/\0//g; $HOME_PHONE=~s/\.\.//g; $HOME_PHONE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$WORK_PHONE=~s/\0//g; $WORK_PHONE=~s/\.\.//g; $WORK_PHONE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$EM=~s/\0//g; $EM=~s/\.\.//g; $EM=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SER_PASSPORT=~s/\0//g; $SER_PASSPORT=~s/\.\.//g; $SER_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SOURCE_ABOUT_US=~s/\0//g; $SOURCE_ABOUT_US=~s/\.\.//g; $SOURCE_ABOUT_US=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DATE_OF_FILLING=~s/\0//g; $DATE_OF_FILLING=~s/\.\.//g; $DATE_OF_FILLING=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FIO_PARENT=~s/\0//g; $FIO_PARENT=~s/\.\.//g; $FIO_PARENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$NUM_PASSPORT_PARENT=~s/\0//g; $NUM_PASSPORT_PARENT=~s/\.\.//g; $NUM_PASSPORT_PARENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SER_PASSPORT_PARENT=~s/\0//g; $SER_PASSPORT_PARENT=~s/\.\.//g; $SER_PASSPORT_PARENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KEM_VIDAN_PASSPORT_PARENT=~s/\0//g; $KEM_VIDAN_PASSPORT_PARENT=~s/\.\.//g; $KEM_VIDAN_PASSPORT_PARENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KOGDA_VIDAN_PASSPORT_PARENT=~s/\0//g; $KOGDA_VIDAN_PASSPORT_PARENT=~s/\.\.//g; $KOGDA_VIDAN_PASSPORT_PARENT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$NUM_PASSPORT=~s/\0//g; $NUM_PASSPORT=~s/\.\.//g; $NUM_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KEM_VIDAN_PASSPORT=~s/\0//g; $KEM_VIDAN_PASSPORT=~s/\.\.//g; $KEM_VIDAN_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KOGDA_VIDAN_PASSPORT=~s/\0//g; $KOGDA_VIDAN_PASSPORT=~s/\.\.//g; $KOGDA_VIDAN_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SEX=~s/\0//g; $SEX=~s/\.\.//g; $SEX=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$BRANCH=~s/\0//g; $BRANCH=~s/\.\.//g; $BRANCH=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$MOBILE_PHONE_CHILD=~s/\0//g; $MOBILE_PHONE_CHILD=~s/\.\.//g; $MOBILE_PHONE_CHILD=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$STUDENT_INTERESTS=~s/\0//g; $STUDENT_INTERESTS=~s/\.\.//g; $STUDENT_INTERESTS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$AGREE_GET_SMS=~s/\0//g; $AGREE_GET_SMS=~s/\.\.//g; $AGREE_GET_SMS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$AGREE_GET_EMAIL=~s/\0//g; $AGREE_GET_EMAIL=~s/\.\.//g; $AGREE_GET_EMAIL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$AGREE_USE_PHOTO=~s/\0//g; $AGREE_USE_PHOTO=~s/\.\.//g; $AGREE_USE_PHOTO=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$BARTER=~s/\0//g; $BARTER=~s/\.\.//g; $BARTER=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$INDIVIDUAL=~s/\0//g; $INDIVIDUAL=~s/\.\.//g; $INDIVIDUAL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Перекодировка
Encode::from_to($FIO_STUDENT,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($FIO_PARENT,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($PLACE_WORK_STUDY,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($POSITION_FACULTET,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($HOME_ADDR,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($EM,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($SOURCE_ABOUT_US,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($KEM_VIDAN_PASSPORT_PARENT,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($KEM_VIDAN_PASSPORT,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($SEX,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($BRANCH,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($STUDENT_INTERESTS,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
###########################

########Проверка на ввод ФИО
if (length($FIO_STUDENT)==0)
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

########Проверка длинны ФИО
if (length($FIO_STUDENT)>255)
{
  my $ans="ФИО не может быть длиннее 255 символов!";
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

########Проверка на ввод даты рождения
if (length($DATE_OF_BORN)==0)
{
  my $ans="Дату рождения необходимо заполнить!";
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

########Проверка на ввод пола
if (length($SEX)==0)
{
  my $ans="Необходимо заполнить \"Пол\"!";
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

########Проверка на ввод букв М или Ж
if ($SEX ne "М" && $SEX ne "Ж")
{
  my $ans="Пол может быть только М или Ж";
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

########Проверка на ввод адреса
if (length($HOME_ADDR)==0)
{
  my $ans="Необходимо заполнить \"Домашний адрес\"!";
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

########Проверка длинны адреса
if (length($HOME_ADDR)>255)
{
  my $ans="Поле \"Домашний адрес\" не может быть более 255 символов!";
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

########Проверка длинны моб телефона
if (length($MOBILE_PHONE)>20)
{
  my $ans="Поле \"Мобильный телефон\" не может быть более 20 символов!";
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

########Проверка длинны дом телефона
if (length($HOME_PHONE)>20)
{
  my $ans="Поле \"Домашний телефон\" не может быть более 20 символов!";
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

########Проверка длинны раб. телефона
if (length($WORK_PHONE)>20)
{
  my $ans="Поле \"Рабочий телефон\" не может быть более 20 символов!";
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

########Проверка длинны моб. телефона ребенка
if (length($MOBILE_PHONE_CHILD)>20)
{
  my $ans="Поле \"Мобильный телефон ребенка\" не может быть более 20 символов!";
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

########Проверка длинны Email
if (length($EM)>255)
{
  my $ans="Поле \"E-mail\" не может быть более 255 символов!";
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

########Проверка длинны поля Мсето работы/учебы
if (length($PLACE_WORK_STUDY)>255)
{
  my $ans="Поле \"Место работы/учебы\" не может быть более 255 символов!";
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

########Проверка длинны поля должность факультет
if (length($POSITION_FACULTET)>255)
{
  my $ans="Поле \"Должность/факультет\" не может быть более 255 символов!";
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

########Проверка на ввод филиала
if (length($BRANCH)==0)
{
  my $ans="Поле \"Филиал\" необходимо заполнить!";
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

########Проверка на ввод даты заполнения
if (length($DATE_OF_FILLING)==0)
{
  my $ans="Поле \"Дата заполнения\" необходимо заполнить!";
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

my $sql_br="select ID from branches where ID=?";
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($BRANCH);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Наименование филиала необходимо выбирать только из списка!";
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

########Проверка на ввод Только корректных источников информации
if (length($SOURCE_ABOUT_US)>0)
{
 my $dbh_sr=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
 my $sth_sr=$dbh_sr->do("SET NAMES 'cp1251'");

 my $sql_sr="select ID from source_about_us where ID=?";
 $sth_sr=$dbh_sr->prepare($sql_sr);
 $sth_sr->execute($SOURCE_ABOUT_US);
 my $cnt_sr=$sth_sr->rows();
 $dbh_sr->disconnect();

 if ($cnt_sr==0)
 {
  my $ans="Наименование источника необходимо выбирать только из списка!";
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



#Проверяем, если поле "ФИО родителя" заполнено, то вставляем данные с информацией о родителе (а инфу о паспортных данных студента не вставляем), если нет, то наоборот
if ($FIO_PARENT ne "")
{
  
########Проверка н ввод ФИО родителя
if (length($FIO_PARENT)==0)
{
  my $ans="Необходимо заполнить поле \"ФИО родителя\"!";
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

########Проверка длинны поля ФИО родителя
if (length($FIO_PARENT)>100)
{
  my $ans="Поле \"ФИО родителя\" не может быть более 100 символов!";
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

########Проверка на ввод серии паспорта родителя
if (length($SER_PASSPORT_PARENT)==0)
{
  my $ans="Необходимо заполнить поле \"Серия паспорта родителя\"!";
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

########Проверка длинны серии паспорта родителя
if (length($SER_PASSPORT_PARENT)>4)
{
  my $ans="Серия паспорта родителя не может быть более 4 цифр!";
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

########Проверка на ввод номера паспорта родителя
if (length($NUM_PASSPORT_PARENT)==0)
{
  my $ans="Необходимо заполнить поле \"Номер паспорта родителя\"!";
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

########Проверка длинны номера паспорта родителя
if (length($NUM_PASSPORT_PARENT)>6)
{
  my $ans="Номер паспорта родителя не может быть более 6 цифр!";
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

########Проверка на заполнение поля "Кем выдан паспорт"
if (length($KEM_VIDAN_PASSPORT_PARENT)==0)
{
  my $ans="Необходимо заполнить поле \"Кем выдан паспорт родителя\"!";
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

########Проверка длинны поля "Кем выдан паспорт"
if (length($KEM_VIDAN_PASSPORT_PARENT)>255)
{
  my $ans="Поле \"Кем выдан паспорт родителя\" не может быть более 255 символов!";
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

########Проверка на заполнение поля "Когда выдан паспорт родителя"
if (length($KOGDA_VIDAN_PASSPORT_PARENT)==0)
{
  my $ans="Необходимо заполнить поле \"Когда выдан паспорт родителя\"!";
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
  
  
  #Вставляем саму заявку
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into pupils (FIO, DATE_OF_BORN, PLACE_OF_WORK, POSITION_FACULT, HOME_ADDRESS, MOBILE_PHONE, HOME_PHONE, WORK_PHONE, EMAIL, SOURCE_ABOUT_US, DATE_OF_FILLING, FIO_PARENT, NUM_PASSPORT_PARENT, SER_PASSPORT_PARENT, KEM_VIDANO_PASSPORT_PARENT, KOGDA_VIDANO_PASSPORT_PARENT, SEX, BRANCH, USER_ID, MOBILE_CHILD, STUDENT_INTERESTS, AGREMMENT_GET_SMS, AGREMMENT_GET_EMAIL, AGREMMENT_USE_PHOTO, BARTER, INDIVIDUAL) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($FIO_STUDENT, $DATE_OF_BORN, $PLACE_WORK_STUDY, $POSITION_FACULTET, $HOME_ADDR, $MOBILE_PHONE, $HOME_PHONE, $WORK_PHONE, $EM, $SOURCE_ABOUT_US, $DATE_OF_FILLING, $FIO_PARENT, $NUM_PASSPORT_PARENT, $SER_PASSPORT_PARENT, $KEM_VIDAN_PASSPORT_PARENT, $KOGDA_VIDAN_PASSPORT_PARENT, $SEX, $BRANCH, $us_id, $MOBILE_PHONE_CHILD, $STUDENT_INTERESTS, $AGREE_GET_SMS, $AGREE_GET_EMAIL, $AGREE_USE_PHOTO, $BARTER, $INDIVIDUAL);

  $dbh1->disconnect;

  my $ans="Студент добавлен успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################
  exit;
}
else
{  
  
########Проверка на ввод серии паспорта
if (length($SER_PASSPORT)==0)
{
  my $ans="Необходимо заполнить поле \"Серия паспорта\"!";
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

########Проверка длинны серии паспорта
if (length($SER_PASSPORT)>4)
{
  my $ans="Серия паспорта не может быть более 4 цифр!";
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

########Проверка на ввод номера паспорта
if (length($NUM_PASSPORT)==0)
{
  my $ans="Необходимо заполнить поле \"Номер паспорта\"!";
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

########Проверка длинны номера паспорта
if (length($NUM_PASSPORT)>6)
{
  my $ans="Номер паспорта не может быть более 6 цифр!";
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

########Проверка на ввод "Кем видан паспорт"
if (length($KEM_VIDAN_PASSPORT)==0)
{
  my $ans="Необходимо заполнить поле \"Кем выдан паспорт\"!";
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

########Проверка длинны поля "Кем видан паспорт"
if (length($KEM_VIDAN_PASSPORT)>255)
{
  my $ans="Поле \"Кем выдан паспорт\" не может быть длиннее 255 символов!";
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

########Проверка на ввод "Когда выдан паспорт"
if (length($KOGDA_VIDAN_PASSPORT)==0)
{
  my $ans="Необходимо заполнить поле \"Когда выдан паспорт\"!";
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

  
  #Вставляем саму заявку
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into pupils (FIO, DATE_OF_BORN, PLACE_OF_WORK, POSITION_FACULT, HOME_ADDRESS, MOBILE_PHONE, HOME_PHONE, WORK_PHONE, EMAIL, PASSPORT, SOURCE_ABOUT_US, DATE_OF_FILLING, PASSPORT_NUM, PASSPORT_VIDAN, PASSPORT_DATE, SEX, BRANCH, USER_ID, MOBILE_CHILD, STUDENT_INTERESTS, AGREMMENT_GET_SMS, AGREMMENT_GET_EMAIL, AGREMMENT_USE_PHOTO, BARTER, INDIVIDUAL) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($FIO_STUDENT, $DATE_OF_BORN, $PLACE_WORK_STUDY, $POSITION_FACULTET, $HOME_ADDR, $MOBILE_PHONE, $HOME_PHONE, $WORK_PHONE, $EM, $SER_PASSPORT, $SOURCE_ABOUT_US, $DATE_OF_FILLING, $NUM_PASSPORT, $KEM_VIDAN_PASSPORT, $KOGDA_VIDAN_PASSPORT, $SEX, $BRANCH, $us_id, $MOBILE_PHONE_CHILD, $STUDENT_INTERESTS, $AGREE_GET_SMS, $AGREE_GET_EMAIL, $AGREE_USE_PHOTO, $BARTER, $INDIVIDUAL);

  $dbh1->disconnect;

  my $ans="Студент добавлен успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################
  exit;
}

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
