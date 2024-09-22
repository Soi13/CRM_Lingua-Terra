#!/usr/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
#use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;

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
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:a0018982_fin",User=>"a0018982_oleg", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $num_dog=$sess->param('stud_num_dog');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $from=param('from');
my $to=param('to');

$from=~s/\0//g; $from=~s/\.\.//g; $from=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$to=~s/\0//g; $to=~s/\.\.//g; $to=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my $cgi=CGI->new;
my @res;

my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

#my $sql="select ID as 'id', TEXT_MESSAGE as 'text', START_DATE as 'start_date', END_DATE as 'end_date', DETAILS as 'details' from calendar_events where PUPIL_NUM_DOGOVOR=?";
my $sql="select ID as 'id', TEXT_MESSAGE as 'text', START_DATE as 'start_date', END_DATE as 'end_date', DETAILS as 'details' from calendar_pupils where PUPILS_NUM_DOGOVOR=? and START_DATE between ? and ? and END_DATE between ? and ?";
$sth=$dbh->prepare($sql);
$sth->execute($num_dog, $from, $to, $from, $to);
#$sth->execute($num_dog);
$sth->execute();

while ($data=$sth->fetchrow_hashref) {
push @res, $data;
}


$dbh->disconnect;

my $op=JSON->new->pretty(1);
my $json=$op->encode(\@res);

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;


#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://students.linguaterra-soft.ru');
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
else { print "Location: https://students.linguaterra-soft.ru\n\n"; }

__END__