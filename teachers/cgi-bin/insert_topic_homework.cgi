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
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $teacher_id=$sess->param('teacher_id');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {
        
my $ident_gr=param('ident_gr');
my $ident_period=param('ident_period');

$ident_gr=~s/\0//g; $ident_gr=~s/\.\.//g; $ident_gr=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$ident_period=~s/\0//g; $ident_period=~s/\.\.//g; $ident_period=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my @form_fields=(param('DATE_LESSON'), param('TOPIC'), param('HOME_WORK'));

for(my $n=0; $n<=$#form_fields; $n++ )
{
        $form_fields[$n]=~s/\0//g;
        $form_fields[$n]=~s/\.\.//g;
        $form_fields[$n]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        Encode::from_to($form_fields[$n],'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
}


#Проверка корректности даты начала
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($form_fields[0]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата занятия не корректна. Формат должен быть, например, 2016-05-30.";
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
$form_fields[0]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате занятия не корректен месяц. Месяц не может быть больше 12!";
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
$form_fields[0]=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате занятия не разумно большой год.";
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
$form_fields[0]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате занятия не корректно задано число! Число не может быть более 31!";
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


########Проверка на ввод Темы
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить поле \"Тема\"!";
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


########Проверка на длинну Вместимость кабинета
if (length($form_fields[2])==0)
{
  my $ans="Необходимо заполнить поле \"ДЗ\"!";
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


  #Вставляем тему и ДЗ
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into topic_homework (GROUP_ID, PERIOD, DATE_LESSON, TOPIC, HOME_WORK, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?, NOW())";
  $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
  $sth1->execute($ident_gr, $ident_period, $form_fields[0], $form_fields[1], $form_fields[2], $teacher_id);
   
  $dbh1->disconnect;

  my $ans="Тема и ДЗ добавлены успешно!";
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
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://teachers.localhost:6080\n\n"; }
#############################################################

__END__
