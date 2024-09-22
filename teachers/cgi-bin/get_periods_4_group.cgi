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
use Date::Calc qw(:all);
use Time::Local;

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

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $cgi=CGI->new;

my $id_group=param('id_group');
$id_group=~s/\0//g; $id_group=~s/\.\.//g; $id_group=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my @result;

#Определяем Дату начала и окончания срока жизни группы
my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select START_DATE, END_DATE from `groups` where ID=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($id_group);
#В массив записываем извлеченную строку
my @dt_start_end = $sth2->fetchrow_array;
################################################  
  
  
#Создаем помесячную разбивку периодов обучения группы.
my $first_date = $dt_start_end[0];
my $second_date = $dt_start_end[1];
my @f_date = ($first_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
my @s_date = ($second_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
#my $fepoch_dt = timelocal(0,0,0,$f_date[2],$f_date[1]-1,$f_date[0]);
#my $sepoch_dt = timelocal(0,0,0,$s_date[2],$s_date[1]-1,$s_date[0]);
my $fepoch_dt = timelocal(0,0,0,1,$f_date[1]-1,$f_date[0]);
my $sepoch_dt = timelocal(0,0,0,Days_in_Month($s_date[0],$s_date[1]),$s_date[1]-1,$s_date[0]); 
($fepoch_dt,$sepoch_dt) = ($sepoch_dt,$fepoch_dt) if $fepoch_dt > $sepoch_dt;
for (my $i=$fepoch_dt; $i <= $sepoch_dt; $i += 24 * 60 * 60 * 31) 
{
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($i);
  my $period=($mon+1).".".($year+1900);
  
  #Формируем массив для вывода его в Datagrid
  push @result, {"id"=>$period, "text"=>$period};
} 


my $op=JSON->new->pretty(1);
my $json=$op->encode(\@result);

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;

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