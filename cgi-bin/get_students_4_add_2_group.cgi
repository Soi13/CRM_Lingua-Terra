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

my $sort=param('sort');
my $order=param('order');
my $br=param('br');
my $gr=param('gr');
my $erase_filter=param('erase_filter');
my $date_of_dogovor_from=param('date_of_dogovor_from');
my $date_of_dogovor_to=param('date_of_dogovor_to');
my $kind_prog=param('kind_prog');
$br=~s/\0//g; $br=~s/\.\.//g; $br=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$gr=~s/\0//g; $gr=~s/\.\.//g; $gr=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$sort=~s/\0//g; $sort=~s/\.\.//g; $sort=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$order=~s/\0//g; $order=~s/\.\.//g; $order=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$date_of_dogovor_from=~s/\0//g; $date_of_dogovor_from=~s/\.\.//g; $date_of_dogovor_from=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$date_of_dogovor_to=~s/\0//g; $date_of_dogovor_to=~s/\.\.//g; $date_of_dogovor_to=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$kind_prog=~s/\0//g; $kind_prog=~s/\.\.//g; $kind_prog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$erase_filter=~s/\0//g; $erase_filter=~s/\.\.//g; $erase_filter=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

##################Фильтрация по "Дате заключение договра". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список студентов по филиалу, который указан в группе, к которому привязывают студентов.
if (defined($date_of_dogovor_from) && length($date_of_dogovor_from)!=0 && defined($date_of_dogovor_to) && length($date_of_dogovor_to)!=0)
{

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from pupils, document_students where pupils.Num_dogovor not in (select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?) and pupils.BRANCH=? and pupils.Num_dogovor=document_students.PUPILS_Num_dogovor and document_students.DATE_START_DOGOVOR between ? and ?";
$sth=$dbh->prepare($sql);
$sth->execute($gr, $br, $date_of_dogovor_from, $date_of_dogovor_to);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select pupils.Num_dogovor, pupils.FIO, pupils.DATE_OF_BORN from pupils, document_students where pupils.Num_dogovor not in (select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?) and pupils.BRANCH=? and pupils.Num_dogovor=document_students.PUPILS_Num_dogovor and document_students.DATE_START_DOGOVOR between ? and ?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($gr, $br, $date_of_dogovor_from, $date_of_dogovor_to);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

##################Фильтрация по "Проограмма". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список студентов по филиалу, который указан в группе, к которому привязывают студентов.
if (defined($kind_prog) && length($kind_prog)!=0)
{

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from pupils where KIND_PROG_FROM_DOGOVOR=?";
$sth=$dbh->prepare($sql);
$sth->execute($kind_prog);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select pupils.Num_dogovor, pupils.FIO, pupils.DATE_OF_BORN from pupils where KIND_PROG_FROM_DOGOVOR=?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($kind_prog);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from pupils where BRANCH=?";
$sth=$dbh->prepare($sql);
$sth->execute($br);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;
my $sql1="select Num_dogovor, FIO, DATE_OF_BORN from pupils where Num_dogovor not in (select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?) and pupils.BRANCH=? order by $sort $order";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($gr, $br);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

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