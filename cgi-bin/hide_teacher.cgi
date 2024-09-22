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

my $id_teacher=param('id_teacher');
$id_teacher=~s/\0//g; $id_teacher=~s/\.\.//g; $id_teacher=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my @data;
my @teachers_students;
#Определяем привязаны ли к преподу студенты, если да, то скрывать его нельзя!
my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select pupils.FIO from pupils, lessons, groups_students where pupils.Num_dogovor=groups_students.PUPILS_NUM_DOGOVOR and groups_students.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($id_teacher);

#Записываем все в массив
while (@data=$sth2->fetchrow_array) {
push @teachers_students, @data;
}

if (@teachers_students)
{
    my $ans="К преподавателю привязаны студенты: ". join(', ', @teachers_students).". Операцию выполнить невозможно!";
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


#Определяем состояние препода (заблокирован или активен). Исходя из этого будем применять нужный запрос
my $dbh0=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth0=$dbh0->do("SET NAMES 'cp1251'");
my $sql0="select BLOCKED from teachers where ID=?";
$sth0=$dbh0->prepare($sql0);
$sth0->execute($id_teacher);
my @state_teacher = $sth0->fetchrow_array;

my $query;
my $status;

if ($state_teacher[0]==1)
{
   $query="update teachers set BLOCKED=0, ACTIVE_ONLINE_ROOM=1 where ID=?";
   $status="активирован";
}
else
{
   $query="update teachers set BLOCKED=1, ACTIVE_ONLINE_ROOM=0 where ID=?";
   $status="скрыт";
}

my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1=$query;
$sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
$sth1->execute($id_teacher);

$dbh1->disconnect;

my $ans="Преподаватель ".$status." успешно!";
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
