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

my $page=param('page');
my $rows=param('rows');
my $sort=param('sort');
my $order=param('order');
my $fio=param('fio');
my $who_get_zayav=param('who_get_zayav');
my $source_zayav=param('source_zayav');
my $date_of_zayav_from=param('date_of_zayav_from');
my $date_of_zayav_to=param('date_of_zayav_to');
my $age=param('age');
my $date_of_born_from=param('date_of_born_from');
my $date_of_born_to=param('date_of_born_to');
my $branch=param('branch');
my $language=param('language');
my $level_knowledge=param('level_knowledge');
my $date_of_test_from=param('date_of_test_from');
my $date_of_test_to=param('date_of_test_to');
my $erase_filter=param('erase_filter');

$fio=~s/\0//g; $fio=~s/\.\.//g;
$who_get_zayav=~s/\0//g; $who_get_zayav=~s/\.\.//g;
$source_zayav=~s/\0//g; $source_zayav=~s/\.\.//g;
$age=~s/\0//g; $age=~s/\.\.//g;
$date_of_born_from=~s/\0//g; $date_of_born_from=~s/\.\.//g;
$date_of_born_to=~s/\0//g; $date_of_born_to=~s/\.\.//g;
$date_of_zayav_from=~s/\0//g; $date_of_zayav_from=~s/\.\.//g;
$date_of_zayav_to=~s/\0//g; $date_of_zayav_to=~s/\.\.//g;
$branch=~s/\0//g; $branch=~s/\.\.//g;
$language=~s/\0//g; $language=~s/\.\.//g;
$level_knowledge=~s/\0//g; $level_knowledge=~s/\.\.//g;
$date_of_test_from=~s/\0//g; $date_of_test_from=~s/\.\.//g;
$date_of_test_to=~s/\0//g; $date_of_test_to=~s/\.\.//g;
$erase_filter=~s/\0//g; $erase_filter=~s/\.\.//g;

Encode::from_to($fio, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($who_get_zayav, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($source_zayav, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($branch, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($language, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($level_knowledge, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($age, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)


##################Фильтрация по "Кто принял заявку". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($who_get_zayav) && length($who_get_zayav)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where WHO_GET_ZAYAV=?";
$sth=$dbh->prepare($sql);
$sth->execute($who_get_zayav);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.WHO_GET_ZAYAV=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($who_get_zayav, $offset, $rows);

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


##################Фильтрация по "Источник заявки". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($source_zayav) && length($source_zayav)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where SOURCE_ZAYAV=?";
$sth=$dbh->prepare($sql);
$sth->execute($source_zayav);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.SOURCE_ZAYAV=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($source_zayav, $offset, $rows);

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


##################Фильтрация по "Дата заявки". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($date_of_zayav_from) && length($date_of_zayav_from)!=0 && defined($date_of_zayav_to) && length($date_of_zayav_to)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where DATE_GET_ZAYAV between ? and ?";
$sth=$dbh->prepare($sql);
$sth->execute($date_of_zayav_from, $date_of_zayav_to);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.DATE_GET_ZAYAV between ? and ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($date_of_zayav_from, $date_of_zayav_to, $offset, $rows);

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


##################Фильтрация по "Возраст студента". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($age) && length($age)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where AGE_STUDENT like ?";
$sth=$dbh->prepare($sql);
$sth->execute($age);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.AGE_STUDENT like ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($age, $offset, $rows);

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

##################Фильтрация по "Дата рождения". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($date_of_born_from) && length($date_of_born_from)!=0 && defined($date_of_born_to) && length($date_of_born_to)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where DATE_OF_BORN between ? and ?";
$sth=$dbh->prepare($sql);
$sth->execute($date_of_born_from, $date_of_born_to);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.DATE_OF_BORN between ? and ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($date_of_born_from, $date_of_born_to, $offset, $rows);

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


##################Фильтрация по "Филиал". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($branch) && length($branch)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where BRANCH=?";
$sth=$dbh->prepare($sql);
$sth->execute($branch);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.BRANCH=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($branch, $offset, $rows);

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

##################Фильтрация по "Язык". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($language) && length($language)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where LANGUAGE=?";
$sth=$dbh->prepare($sql);
$sth->execute($language);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.LANGUAGE=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($language, $offset, $rows);

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

##################Фильтрация по "Уровень владения". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($level_knowledge) && length($level_knowledge)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where LEVEL_KNOWLEDGE=?";
$sth=$dbh->prepare($sql);
$sth->execute($level_knowledge);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.LEVEL_KNOWLEDGE=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($level_knowledge, $offset, $rows);

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

##################Фильтрация по "Дате тестирования". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($date_of_test_from) && length($date_of_test_from)!=0 && defined($date_of_test_to) && length($date_of_test_to)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where DATE_OF_TEST between ? and ?";
$sth=$dbh->prepare($sql);
$sth->execute($date_of_test_from, $date_of_test_to);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.DATE_OF_TEST between ? and ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($date_of_test_from, $date_of_test_to, $offset, $rows);

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

##################Фильтрация по "Снять все фильтры". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($erase_filter) && length($erase_filter)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($offset, $rows);

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

#Если ФИО определено, передано и оно не равно 0, то выполняем поиск
if (defined($fio) && length($fio)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv where FIO_STUDENT like ?";
$sth=$dbh->prepare($sql);
$sth->execute('%'.$fio.'%');

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID where zayavki_reserv.FIO_STUDENT like ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute('%'.$fio.'%', $offset, $rows);

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
else #Иначе ФИО не определено, не передано и оно равно 0, то показываем весь список студентов
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from zayavki_reserv";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select zayavki_reserv.*, kind_languages.LANGUAGE as LANG, level_knowledge.LEVEL, branches.BRANCH as BR from zayavki_reserv left join kind_languages on zayavki_reserv.LANGUAGE=kind_languages.ID  left join level_knowledge on zayavki_reserv.LEVEL_KNOWLEDGE=level_knowledge.ID left join branches on zayavki_reserv.BRANCH=branches.ID order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($offset, $rows);

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