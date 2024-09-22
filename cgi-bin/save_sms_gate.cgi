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
use Digest::MD5 qw(md5_hex);


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

my $SMS_GATE_LOGIN=param('SMS_GATE_LOGIN');
my $SMS_GATE_PSW=param('SMS_GATE_PSW');

$SMS_GATE_LOGIN=~s/\0//g; $SMS_GATE_LOGIN=~s/\.\.//g; $SMS_GATE_LOGIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SMS_GATE_PSW=~s/\0//g; $SMS_GATE_PSW=~s/\.\.//g; $SMS_GATE_PSW=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Перекодировка
Encode::from_to($SMS_GATE_LOGIN, 'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($SMS_GATE_PSW, 'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
###########################

########Проверка на ввод логина
if (length($SMS_GATE_LOGIN)==0)
{
  my $ans="Необходимо заполнить \"Логин\"!";
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

########Проверка длинны логина
if (length($SMS_GATE_LOGIN)>50)
{
  my $ans="Логин не может быть длиннее 50 символов!";
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

########Проверка на ввод пароля
if (length($SMS_GATE_PSW)==0)
{
  my $ans="Необходимо заполнить \"Пароль\"!";
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

########Проверка на длинну пароля
if (length($SMS_GATE_PSW)>100)
{
  my $ans="\"Пароль\" не может быть длиннее 100 символов!";
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


#Определяем, есть ли уже сохраненные данные SMS шлюза в таблице. Если есть, то просто обновляем строку, если нет и таблица пуста, то вставляем одну строку.
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select * from sms_gate";
$sth1=$dbh1->prepare($sql1);
$sth1->execute();
#В массив записываем извлеченную строку
my @row_gate = $sth1->fetchrow_array;
$dbh1->disconnect;
################################################

if (!@row_gate)
{
  #Вставляем данные SMS - шлюза
  my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="insert into sms_gate (LOGIN, PASSW) values (?,?)";
  $sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
  $sth2->execute($SMS_GATE_LOGIN, $SMS_GATE_PSW);
  $dbh2->disconnect;      
  
}
else
{
  #Обновляем данные SMS - шлюза
  my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="update sms_gate set LOGIN=?, PASSW=?";
  $sth3=$dbh3->prepare($sql3); #Для операций которые не возвращают значение
  $sth3->execute($SMS_GATE_LOGIN, $SMS_GATE_PSW);
  $dbh3->disconnect;      
  
}  
  
my $ans="Данные сохранены успешно!";
#Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
############################################################
exit;


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
