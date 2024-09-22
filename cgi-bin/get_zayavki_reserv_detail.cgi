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

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {


my $id=param('id_z');

my $cgi=CGI->new;
my @res;

my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sth1=$dbh->do("SET NAMES 'cp1251'");
my $sth2=$dbh->do("SET NAMES 'cp1251'");
my $sth3=$dbh->do("SET NAMES 'cp1251'");
my $sth4=$dbh->do("SET NAMES 'cp1251'");
my $sth5=$dbh->do("SET NAMES 'cp1251'");
my $sth6=$dbh->do("SET NAMES 'cp1251'");
my $sth7=$dbh->do("SET NAMES 'cp1251'");
my $sth8=$dbh->do("SET NAMES 'cp1251'");
my $sth10=$dbh->do("SET NAMES 'cp1251'");


my $sql="select 'Дата получения заявки' as 'name', DATE_GET_ZAYAV as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";
my $sql1="select 'Кто принял заявку' as 'name', users_get_zayav.FIO as 'value', 'Подробная информация' as 'group' from zayavki_reserv, users_get_zayav where zayavki_reserv.WHO_GET_ZAYAV=users_get_zayav.ID and zayavki_reserv.ID like ?";
my $sql2="select 'Источник заявки' as 'name', source_zayav.SOURCE as 'value', 'Подробная информация' as 'group' from zayavki_reserv, source_zayav where zayavki_reserv.SOURCE_ZAYAV=source_zayav.ID and zayavki_reserv.ID like ?";
my $sql3="select 'Телефон' as 'name', PHONE as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";
my $sql4="select 'ФИО родителя' as 'name', FIO_PARENT as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";
my $sql5="select 'Откуда о нас узнали' as 'name', source_about_us.SOURCE as 'value', 'Подробная информация' as 'group' from zayavki_reserv, source_about_us where zayavki_reserv.SOURCE_ABOUT_US=source_about_us.ID and zayavki_reserv.ID like ?";
my $sql6="select 'Дата тестирования' as 'name', DATE_OF_TEST as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";
my $sql7="select 'Время тестирования' as 'name', TIME_OF_TEST as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";
my $sql8="select 'Заметки' as 'name', NOTES as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";
my $sql10="select 'Дата рождения' as 'name', DATE_OF_BORN as 'value', 'Подробная информация' as 'group' from zayavki_reserv where ID like ?";


$sth=$dbh->prepare($sql);
$sth1=$dbh->prepare($sql1);
$sth2=$dbh->prepare($sql2);
$sth3=$dbh->prepare($sql3);
$sth4=$dbh->prepare($sql4);
$sth5=$dbh->prepare($sql5);
$sth6=$dbh->prepare($sql6);
$sth7=$dbh->prepare($sql7);
$sth8=$dbh->prepare($sql8);
$sth10=$dbh->prepare($sql10);


$sth->execute($id);
$sth1->execute($id);
$sth2->execute($id);
$sth3->execute($id);
$sth4->execute($id);
$sth5->execute($id);
$sth6->execute($id);
$sth7->execute($id);
$sth8->execute($id);
$sth10->execute($id);


while ($data=$sth->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth1->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth2->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth3->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth4->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth5->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth6->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth7->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth8->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth10->fetchrow_hashref) {
push @res, $data;
}

$dbh->disconnect;

my $op=JSON->new->pretty(1);
my $json=$op->encode({ rows=> \@res, total => 4 });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://linguaterra-soft.ru');
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
else { print "Location: http://localhost:6080\n\n"; }


__END__