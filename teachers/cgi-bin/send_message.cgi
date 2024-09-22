#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Net::SMTP;
use Net::SMTP_auth;
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
#Создаем массив полей переданных из формы

my @form_fields=(param('TOPIC_MESSAGE'), param('TEXT_OF_DOCUMENT'));

foreach my $n (@form_fields)
{
        $n=~s/\0//g;
        $n=~s/\.\.//g;
        $n=~s/<script>(.*[\s\S]*?)\<\/script>//gs; #Удаление текста между тегами Script
        $n=~s/<script>|<\/script>|script|\/script//gs; #Удаление самих тегов Script
        Encode::from_to($n,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
}

########Проверка на ввод Темы сообщения
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить поле \"Тема сообщения\"!";
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




########Проверка на вводе текста сообщения
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить поле \"Текст сообщения\"!";
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


#Определяем ФИО препода по его ID
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select FIO from teachers where ID=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id);
#В массив записываем извлеченную строку
my @teacher_fio = $sth->fetchrow_array;

#Вставляем сообщение в БД
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="insert into support_messages (TOPIC, TEXT_MESSAGE, USER_ID, DATETIME_CREATE) values (?,?,?, NOW())";
$sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
$sth1->execute($teacher_fio[0]." - ".$form_fields[0], $form_fields[1], $teacher_id);
$dbh1->disconnect;


my $smtp = Net::SMTP_auth->new('smtp.lingua-terra.ru', Timeout => 20, Debug => 1, Port=>587) or die "Couldn't connect to server; $!"; 
$smtp->auth('LOGIN','robot@lingua-terra.ru','lingua');
$smtp->mail('robot@lingua-terra.ru');
my @to = qw(skvortsov@lingua-terra.ru);
foreach my $rcpt (@to)
{
$smtp->to($rcpt);
}
$smtp->data();
$smtp->datasend("Subject: ".$teacher_fio[0]." - ".$form_fields[0]."\n");
$smtp->datasend("To: skvortsov\@lingua-terra.ru\n");
$smtp->datasend("From: robot\@lingua-terra.ru\n");
$smtp->datasend("Content-Type: text/html; charset=\"windows-1251\"\n\n");
$smtp->datasend("\n");
$smtp->datasend($form_fields[1]);
$smtp->datasend("\n");
$smtp->quit;


  my $ans="Сообщение отправлено успешно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;


  
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
