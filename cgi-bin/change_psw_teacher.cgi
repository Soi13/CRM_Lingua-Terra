#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use ConnectDB;
use JSON;
use Encode;
use Lingua::Translit;

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

######Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass))
{

my $id_u=$cgi->param('id_u');
my $psw1=$cgi->param('USER_PSW1');
my $psw2=$cgi->param('USER_PSW2');

$id_u=~s/\0//g; $id_u=~s/\.\.//g; $id_u=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$psw1=~s/\0//g; $psw1=~s/\.\.//g; $psw1=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$psw2=~s/\0//g; $psw2=~s/\.\.//g; $psw2=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#######Проверка на заполнение паролей.
if ((length($psw1)==0) || (length($psw2)==0))
{
  my $ans="Один из паролей пустой! Заполните поле.";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

#######Если новые пароли не совпадают, уведомляем пользователя.
if ($psw1 ne $psw2)
{
  my $ans="Введенные пароли не совпадают!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

######Если пароль не отвечает правилу сложности, то выводим сообщение пользователю
if (($psw1!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm) && ($psw2!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm))
{
  my $ans="Введенный пароль не соответствует требованиям сложности! Пароль должен иметь длинну от 8 до 20 символов, содержать хотя бы одну цифру, одну букву заглавную и прописную, а также содержать один из символов (@#\$%!).";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

#######Определение наиболее старой записи в старых паролях студента, для ее update
my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="select FIO from teachers where ID=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($id_u);
#В массив записываем извлеченную строку
my @row_fio = $sth4->fetchrow_array;
##############################################

my @surname=split(' ', $row_fio[0]); #Разбиваем ФИО на отдельные части, чтобы извлечь только фамилию для ее транслитерации
Encode::from_to($surname[0],'windows-1251','utf8');
my $str = $surname[0];	
my $tr = new Lingua::Translit("GOST 7.79 RUS");
my $result_tr;
if ($tr->can_reverse()) {
    $result_tr = $tr->translit($str);
}

###########Меняем пароль, предварительно шифруя его
my $md5_psw=md5_hex($psw1); # Шифруем пароль
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="update teachers set LOGIN=?, PASSW=?, PASSW_DAYS_OF_LIVE=?, PASSW_DATE_EXPIRED=ADDDATE(NOW(), ?), ACTIVE_ONLINE_ROOM=? where ID like ?";
$sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
$sth1->execute($result_tr, $md5_psw, 40, 40, 1, $id_u);
$dbh1->disconnect;

my $ans="Пароль добавлен/заменен успешно! Логин:".$surname[0]."; Пароль:".$psw1;
#Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
exit();
##############################################################

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



