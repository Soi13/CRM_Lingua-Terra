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

my $num=param('num');
$num=~s/\0//g; $num=~s/\.\.//g; $num=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

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
my $sth9=$dbh->do("SET NAMES 'cp1251'");
my $sth11=$dbh->do("SET NAMES 'cp1251'");
my $sth12=$dbh->do("SET NAMES 'cp1251'");

my $sql="select 'Дата рождения' as 'name', DATE_OF_BORN as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql1="select 'Серия паспорта' as 'name', SER_PASSPORT as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql2="select 'Номер паспорта' as 'name', NUM_PASSPORT as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql3="select 'Кем выдан' as 'name', KEM_VIDAN as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql4="select 'Когда выдан' as 'name', KOGDA_VIDAN as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql5="select 'Код подразделения' as 'name', KOD_PODRAZDELEN as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql6="select 'ИНН' as 'name', INN as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql7="select 'СНИЛС' as 'name', SNILS as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql8="select 'Дом. адрес' as 'name', HOME_ADDRESS as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql9="select 'Дата трудового договора' as 'name', DATE_WORK_DOGOVOR as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql12="select 'Согласие на получение Email' as 'name', IF(AGREMMENT_GET_EMAIL=1,'Да','Нет') as 'value', 'Основные данные' as 'group' from teachers where ID like ?";
my $sql11="select 'Ребенок' as 'name', CONCAT (children_of_teachers.FIO, '; День рожд.: ', children_of_teachers.DATE_OF_BORN) as 'value', 'Данные о детях' as 'group' from children_of_teachers, teachers where children_of_teachers.UUID_IND_TEACHERS=teachers.UUID_IND and teachers.ID like ?";

$sth=$dbh->prepare($sql);
$sth1=$dbh->prepare($sql1);
$sth2=$dbh->prepare($sql2);
$sth3=$dbh->prepare($sql3);
$sth4=$dbh->prepare($sql4);
$sth5=$dbh->prepare($sql5);
$sth6=$dbh->prepare($sql6);
$sth7=$dbh->prepare($sql7);
$sth8=$dbh->prepare($sql8);
$sth9=$dbh->prepare($sql9);
$sth11=$dbh->prepare($sql11);
$sth12=$dbh->prepare($sql12);

$sth->execute($num);
$sth1->execute($num);
$sth2->execute($num);
$sth3->execute($num);
$sth4->execute($num);
$sth5->execute($num);
$sth6->execute($num);
$sth7->execute($num);
$sth8->execute($num);
$sth9->execute($num);
$sth11->execute($num);
$sth12->execute($num);


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
while ($data=$sth9->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth11->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth12->fetchrow_hashref) {
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