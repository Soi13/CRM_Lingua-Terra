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

my $idd=param('id_x2');  
$idd=~s/\0//g; $idd=~s/\.\.//g;

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

  ################################### По ID определяем заявку и извлекаем все поля и записываем их в массив   @row_zayav для вставки их в таблицу pupils
  my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  my $sql="select * from zayavki where ID=?";
  $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
  $sth->execute($idd);
  #В массив записываем извлеченную строку
  my @row_zayav = $sth->fetchrow_array;  
  ################################################
  

  ###################################Вставляем данные из заявки в таблицу zayavki_reserv и затем удаляем заявку из таблицы zayavki
  #Используем метод транзакций и блок Eval с переменной $@, если произошла ошибка во время выполнения SQL команд в блоке Eval, то выполняем откат операций
  
  my $dbh2=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  eval {  
  #Вставляем/переносим данные из заявки в таблицу pupils
  my $sql2="insert into zayavki_reserv (DATE_GET_ZAYAV, WHO_GET_ZAYAV, SOURCE_ZAYAV, FIO_STUDENT, FIO_PARENT, AGE_STUDENT, LANGUAGE, LEVEL_KNOWLEDGE, BRANCH, PHONE, SOURCE_ABOUT_US, DATE_OF_TEST, TIME_OF_TEST, NOTES, USER_ID, UUID_IND, DATE_OF_BORN, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,NOW())";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($row_zayav[1], $row_zayav[2], $row_zayav[3], $row_zayav[4], $row_zayav[5], $row_zayav[6], $row_zayav[7], $row_zayav[8], $row_zayav[9], $row_zayav[10], $row_zayav[11], $row_zayav[12], $row_zayav[13], $row_zayav[14], $us_id, $row_zayav[16], $row_zayav[17]);
   
  #Удаление перенесенной заявки из таблицы zayavki
  $sql2="delete from zayavki where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($idd);
  
  $dbh2->commit; #Завершение транзакции
  $dbh2->{AutoCommit}=1; 
  $dbh2->{RaiseError}=0;
  };
  if ($@) # если произошла ошибка, то откатываем транзакцию
  {
  # откат внутри eval, чтобы ошибка отката не привела к завершению работы сценария
  eval { $dbh2->rollback; };
  }
  $dbh2->disconnect; 
  ################################################

  my $ans="true";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({success => $res});

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
