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

###############Получение массива имен и ДР детей вводимого препода. Для этого используется поле DATA_CHILD. Они передается как массивы значений.
my $query=CGI->new;
my @DATA_CHILD = $query->param('DATA_CHILD');

for(my $n=0; $n<=$#DATA_CHILD; $n++ )
{
        $DATA_CHILD[$n]=~s/\0//g;
        $DATA_CHILD[$n]=~s/\.\.//g;
        $DATA_CHILD[$n]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        Encode::from_to($DATA_CHILD[$n],'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
}
####################


################Получение остальных полей
my $FIO=param('FIO');
my $POSITION=param('POSITION');
my $PHONE=param('PHONE');
my $EMAIL=param('EMAIL');
my $DATE_OF_BORN=param('DATE_OF_BORN');
my $SER_PASSPORT=param('SER_PASSPORT');
my $NUM_PASSPORT=param('NUM_PASSPORT');
my $KEM_VIDAN=param('KEM_VIDAN');
my $KOGDA_VIDAN=param('KOGDA_VIDAN');
my $KOD_PODRAZDELEN=param('KOD_PODRAZDELEN');
my $INN=param('INN');
my $SNILS=param('SNILS');
my $HOME_ADDRESS=param('HOME_ADDRESS');
my $DATE_WORK_DOGOVOR=param('DATE_WORK_DOGOVOR');
my $AGREMMENT_GET_EMAIL=param('AGREMMENT_GET_EMAIL');

$FIO=~s/\0//g; $FIO=~s/\.\.//g; $FIO=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$POSITION=~s/\0//g; $POSITION=~s/\.\.//g; $POSITION=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PHONE=~s/\0//g; $PHONE=~s/\.\.//g; $PHONE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$EMAIL=~s/\0//g; $EMAIL=~s/\.\.//g; $EMAIL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DATE_OF_BORN=~s/\0//g; $DATE_OF_BORN=~s/\.\.//g; $DATE_OF_BORN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SER_PASSPORT=~s/\0//g; $SER_PASSPORT=~s/\.\.//g; $SER_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$NUM_PASSPORT=~s/\0//g; $NUM_PASSPORT=~s/\.\.//g; $NUM_PASSPORT=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KEM_VIDAN=~s/\0//g; $KEM_VIDAN=~s/\.\.//g; $KEM_VIDAN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KOGDA_VIDAN=~s/\0//g; $KOGDA_VIDAN=~s/\.\.//g; $KOGDA_VIDAN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$KOD_PODRAZDELEN=~s/\0//g; $KOD_PODRAZDELEN=~s/\.\.//g; $KOD_PODRAZDELEN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$INN=~s/\0//g; $INN=~s/\.\.//g; $INN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SNILS=~s/\0//g; $SNILS=~s/\.\.//g; $SNILS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$HOME_ADDRESS=~s/\0//g; $HOME_ADDRESS=~s/\.\.//g; $HOME_ADDRESS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DATE_WORK_DOGOVOR=~s/\0//g; $DATE_WORK_DOGOVOR=~s/\.\.//g; $DATE_WORK_DOGOVOR=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$AGREMMENT_GET_EMAIL=~s/\0//g; $AGREMMENT_GET_EMAIL=~s/\.\.//g; $AGREMMENT_GET_EMAIL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($FIO,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($POSITION,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($PHONE,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($EMAIL,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($DATE_OF_BORN,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($SER_PASSPORT,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($NUM_PASSPORT,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($KEM_VIDAN,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($KOGDA_VIDAN,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($KOD_PODRAZDELEN,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($INN,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($SNILS,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($HOME_ADDRESS,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($DATE_WORK_DOGOVOR,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($AGREMMENT_GET_EMAIL,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно


########Проверка на ввод ФИО
if (length($FIO)==0)
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
if (length($FIO)>255)
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

########Проверка на ввод должности
if (length($POSITION)==0)
{
  my $ans="Необходимо заполнить \"Должность\"!";
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

########Проверка длинны должности
if (length($POSITION)>255)
{
  my $ans="Должность не может быть длиннее 255 символов!";
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

########Проверка на ввод телефона
if (length($PHONE)==0)
{
  my $ans="Необходимо заполнить \"Телефон\"!";
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

########Проверка корректности Телефона
#if (length($PHONE)>0)
#{
#  if ($PHONE!~m/^((8|\+7)[\- ]?)?(\(?\d{2,5}\)?[\- ]?)?[\d\- ]{7,10}$/is)
#  {
#        my $ans="Формат телефонного номера не корректен!";
#        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
#        my $res=$ans;

#        #convert  data to JSON
#        my $op = JSON -> new -> pretty(1);
#        my $json = $op -> encode({result => $res});

#        print $cgi->header('application/json;charset=windows-1251');
#        print $json;
#        exit;
#  }
#}
##############################################################

########Проверка длинны телефона
if (length($PHONE)>20)
{
  my $ans="Телефон не может быть длиннее 20 символов!";
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

########Проверка корректности E-Mail
if (length($EMAIL)>0)
{
  if ($EMAIL!~ /^[a-z0-9\.\-_]+\@[a-z0-9\.\-_]+\.[a-z]{2,4}$/i)
  {
        my $ans="Введенный EMAIL не корректен!";
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

########Проверка на ввод ДР препода
if (length($DATE_OF_BORN)==0)
{
  my $ans="Необходимо заполнить \"Дату рождения преподавателя\"!";
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
if ($DATE_OF_BORN!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата ДР преподавателя не корректна. Формат должен быть, например, 2016-05-30.";
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
$DATE_OF_BORN=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате ДР преподавателя не корректен месяц. Месяц не может быть больше 12!";
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
$DATE_OF_BORN=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате ДР преподавателя не разумно большой год.";
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
$DATE_OF_BORN=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате ДР преподавателя не корректно задано число! Число не может быть более 31!";
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

########Проверка на ввод серии паспорта 
#if (length($SER_PASSPORT)==0)
#{
#  my $ans="Необходимо заполнить \"Серию паспорта\"!";
#  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
#  my $res=$ans;

#  #convert  data to JSON
#  my $op = JSON -> new -> pretty(1);
#  my $json = $op -> encode({result => $res});

#  print $cgi->header('application/json;charset=windows-1251');
#  print $json;
#  exit;
#}
##############################################################

########Проверка длинны серии паспорта
#if (length($SER_PASSPORT)>4)
#{
#  my $ans="Серия паспорта не может быть длиннее 4 символов!";
#  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
#  my $res=$ans;

#  #convert  data to JSON
#  my $op = JSON -> new -> pretty(1);
#  my $json = $op -> encode({result => $res});

#  print $cgi->header('application/json;charset=windows-1251');
#  print $json;
#  exit;
#}
##############################################################

########Проверка на ввод только цифр в серии паспорта
if ($SER_PASSPORT!~m/^\d+$/is)
{
  my $ans="Серия паспорта может содержать только цифры!";
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
  my $ans="Необходимо заполнить \"Номер паспорта\"!";
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
  my $ans="Номер паспорта не может быть длиннее 6 символов!";
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

########Проверка на ввод только цифр в номере паспорта
if ($NUM_PASSPORT!~m/^\d+$/is)
{
  my $ans="Номер паспорта может содержать только цифры!";
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

########Проверка на ввод кем выдан паспорт 
#if (length($KEM_VIDAN)==0)
#{
#  my $ans="Необходимо заполнить \"Кем выдан паспорт\"!";
#  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
#  my $res=$ans;

#  #convert  data to JSON
#  my $op = JSON -> new -> pretty(1);
#  my $json = $op -> encode({result => $res});

#  print $cgi->header('application/json;charset=windows-1251');
#  print $json;
#  exit;
#}
##############################################################

########Проверка длинны кем выдан паспорт
if (length($KEM_VIDAN)>255)
{
  my $ans="Кем выдан паспорт не может быть длиннее 255 символов!";
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

########Проверка на ввод даты выдачи паспорта
if (length($KOGDA_VIDAN)==0)
{
  my $ans="Необходимо заполнить \"Дату выдачи паспорта\"!";
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

#Проверка корректности даты выдачи
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($KOGDA_VIDAN!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата выдачи паспорта не корректна. Формат должен быть, например, 2016-05-30.";
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
# Разбираем дату на день месяу и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$KOGDA_VIDAN=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате выдачи паспорта не корректен месяц. Месяц не может быть больше 12!";
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
$KOGDA_VIDAN=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате выдачи паспорта не разумно большой год.";
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
$KOGDA_VIDAN=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате выдачи паспорта не корректно задано число! Число не может быть более 31!";
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

########Проверка длинны кода подразделения
if (length($KOD_PODRAZDELEN)>7)
{
  my $ans="Код подразделения не может быть длиннее 7 символов!";
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

########Проверка длинны ИНН
if (length($INN)>12)
{
  my $ans="ИНН не может быть длиннее 12 символов!";
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

########Проверка корректности ИНН
if (length($INN)>0)
{
  if ($INN!~m/^\d{12}$/ixs)
  {
    my $ans="Введенный ИНН не корректен. ИНН должен состоять из 12 цифр!.";
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

########Проверка длинны СНИЛС
if (length($SNILS)>14)
{
  my $ans="СНИЛС не может быть длиннее 14 символов!";
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

########Проверка корректности СНИЛС
if (length($SNILS)>0)
{
  if ($SNILS!~m/^\d{3}[-]\d{3}[-]\d{3}[\s]\d{2}$/ixs)
  {
    my $ans="Введенный СНИЛС не корректен. СНИЛС должен иметь формат XXX-XXX-XXX XX!.";
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

########Проверка на ввод адреса 
if (length($HOME_ADDRESS)==0)
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
if (length($HOME_ADDRESS)>255)
{
  my $ans="Домашний адрес не может быть длиннее 255 символов!";
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

########Проверка на ввод даты трудового договора
if (length($DATE_WORK_DOGOVOR)==0)
{
  my $ans="Необходимо заполнить \"Дату трудового договора\"!";
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


#Проверка корректности даты трудового договора
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($DATE_WORK_DOGOVOR!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата трудового договора не корректна. Формат должен быть, например, 2016-05-30.";
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
# Разбираем дату на день месяу и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$DATE_WORK_DOGOVOR=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате трудового договора не корректен месяц. Месяц не может быть больше 12!";
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
$DATE_WORK_DOGOVOR=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате трудового договора не разумно большой год.";
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
$DATE_WORK_DOGOVOR=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате трудового договора не корректно задано число! Число не может быть более 31!";
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


#### Если данные массивы не пусты, т.е. значение не равно -1, то выполняем запрос на вставку данных с детьми препода
if ($#DATA_CHILD ne '-1'){

###Проверяем, все ли поля по детям заполнены.
for (my $u=0; $u<=$#DATA_CHILD; $u++)
{
        if (($DATA_CHILD[$u] eq '') || ($DATA_CHILD[$u] eq ' '))
        {
                my $ans="Не полностью заполнена информация о детях!";
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

##Проверяем, корректно ли введены даты ДР детей? Не написал ли туда юзер всякой херни)))
for (my $u1=1; $u1<=$#DATA_CHILD; $u1=$u1+2)
{
        ## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
        if ($DATA_CHILD[$u1]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
        {
                my $ans="Введенная дата ДР у ребенка не корректна. Формат должен быть, например, 2016-05-30";
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
        # Разбираем дату на день месяу и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
        ###########################################################################################################################################
        
        # Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
        $DATA_CHILD[$u1]=~/(?<=-)(\d{2})(?=-)/;
        if ($&>12)
        {
                my $ans="В введенной дате ДР у ребенка не корректен месяц. Месяц не может быть больше 12!";
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
        $DATA_CHILD[$u1]=~/\d{4}/;
        if ($&>3000)
        {
                my $ans="В введенной дате ДР у ребенка не разумно большой год.";
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
        $DATA_CHILD[$u1]=~/(?<=-)(\d{2})$/;
        if ($&>31)
        {
                my $ans="В введенной дате ДР у ребенка не корректно задано число! Число не может быть более 31!";
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


###################################Генерируем UUID для вставки его в таблицу teachers и children_of_teachers. По этому полю будет происходить связь препода и его детей
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #В массив записываем извлеченную строку
  my @row_uuid = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################


  ###################################Вставляем данные в таблицу teachers, затем children_of_teachers и связываем по UUID
  #Используем метод транзакций и блок Eval с переменной $@, если произошла ошибка во время выполнения SQL команд в блоке Eval, то выполняем откат операций
 
  my $dbh2=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  eval {  
  #Вставляем данные в таблицу teachers
  my $sql2="insert into teachers (FIO, POSITION, PHONE, EMAIL, DATE_OF_BORN, SER_PASSPORT, NUM_PASSPORT, KEM_VIDAN, KOGDA_VIDAN, KOD_PODRAZDELEN, INN, SNILS, HOME_ADDRESS, DATE_WORK_DOGOVOR, AGREMMENT_GET_EMAIL, USER_ID, DATETIME_CREATE, UUID_IND) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW(),?)";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($FIO, $POSITION, $PHONE, $EMAIL, $DATE_OF_BORN, $SER_PASSPORT, $NUM_PASSPORT, $KEM_VIDAN, $KOGDA_VIDAN, $KOD_PODRAZDELEN, $INN, $SNILS, $HOME_ADDRESS, $DATE_WORK_DOGOVOR, $AGREMMENT_GET_EMAIL, $us_id, $row_uuid[0]);
    
  #Вставляем инфу по детям преподов в таблицу children_of_teachers
  for (my $p=0; $p<=$#DATA_CHILD; $p=$p+2)
  {
         my $sql2="insert into children_of_teachers (FIO, DATE_OF_BORN, USER_ID, DATETIME_CREATE, UUID_IND_TEACHERS) values (?,?,?,NOW(),?)";
         $sth2=$dbh2->prepare($sql2);
         $sth2->execute($DATA_CHILD[$p], $DATA_CHILD[$p+1], $us_id, $row_uuid[0]);
  }
    
  $dbh2->commit; #Завершение транзакции
  $dbh2->{AutoCommit}=1; 
  $dbh2->{RaiseError}=0;
  };
  if ($@) # если произошла ошибка, то откатываем транзакцию
  {
  # откат внутри eval, чтобы ошибка отката не привела к завершению работы сценария
  eval { $dbh2->rollback; };
  }
  else
  {
    my $ans="Преподаватель и его дети добавлены успешно!"; 
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
  
  $dbh2->disconnect; 
  ################################################
   
}
else # Вставляем препода без детей
{
  ###################################Генерируем UUID для вставки его в таблицу teachers. В принципе здесь он не нужен, т.к. этот UID используется для связи записи о преподе и его детях, а этот блок для вставки препода без детей.
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #В массив записываем извлеченную строку
  my @row_uuid1 = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################
  
  my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="insert into teachers (FIO, POSITION, PHONE, EMAIL, DATE_OF_BORN, SER_PASSPORT, NUM_PASSPORT, KEM_VIDAN, KOGDA_VIDAN, KOD_PODRAZDELEN, INN, SNILS, HOME_ADDRESS, DATE_WORK_DOGOVOR, AGREMMENT_GET_EMAIL, USER_ID, DATETIME_CREATE, UUID_IND) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW(),?)";
  $sth3=$dbh3->prepare($sql3);
  $sth3->execute($FIO, $POSITION, $PHONE, $EMAIL, $DATE_OF_BORN, $SER_PASSPORT, $NUM_PASSPORT, $KEM_VIDAN, $KOGDA_VIDAN, $KOD_PODRAZDELEN, $INN, $SNILS, $HOME_ADDRESS, $DATE_WORK_DOGOVOR, $AGREMMENT_GET_EMAIL, $us_id, $row_uuid1[0]);

  $dbh3->disconnect;

  my $ans="Преподаватель добавлен успешно!";
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
