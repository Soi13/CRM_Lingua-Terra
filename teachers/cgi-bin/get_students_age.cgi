#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
#use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;
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

my $start_y=param('start_y');
my $end_y=param('end_y');

$start_y=~s/\0//g; $start_y=~s/\.\.//g; $start_y=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$end_y=~s/\0//g; $end_y=~s/\.\.//g; $end_y=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

########Проверка на ввод годов рождений
if (length($start_y)==0 || length($end_y)==0)
{
  my $ans="Необходимо заполнить диапазон годов рождений!";
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

########Проверка годов занятий на ввод только 4 цифр
if ($start_y!~m/^\d{4}$/i || $end_y!~m/^\d{4}$/i)
{
  my $ans="Год может содержать только 4 цифры!";
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

########Проверка чтобы начальный год не был больше конечного
if ($start_y>$end_y)
{
  my $ans="Неверно введен диапазон годов. Начальный год не может быть больше конечного!";
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


my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.DATE_OF_BORN as dt_born, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where year(pupils.DATE_OF_BORN) between ? and ? and pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID and lessons.TEACHER_ID=? group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($start_y, $end_y, $teacher_id);
#В массив записываем извлеченную строку
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." чел.</b>", fio_teacher=>"<b>Кол-во:</b>"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();


#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
         print "Set-Cookie: $cookies\n";
#         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !~ m/SID=/) {
                        if ($url !~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }
}
else { print "Location: http://teachers.localhost:6080\n\n"; }

__END__