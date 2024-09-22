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
        print "Location: http://localhost:6080/\n\n";
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
my $room=param('room');

my $room_name=param('room_name');
my $capacity_room=param('capacity_room');
my $branch=param('branch');
my $erase_filter=param('erase_filter');

$room=~s/\0//g; $room=~s/\.\.//g; $room=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$room_name=~s/\0//g; $room_name=~s/\.\.//g; $room_name=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$capacity_room=~s/\0//g; $capacity_room=~s/\.\.//g; $capacity_room=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$branch=~s/\0//g; $branch=~s/\.\.//g; $branch=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$erase_filter=~s/\0//g; $erase_filter=~s/\.\.//g; $erase_filter=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($room, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($room_name, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)
Encode::from_to($capacity_room, 'utf-8', 'cp1251'); #Декодируем переданнуюстроку из utf8 в cp1251 (Windows-1251)

##################Фильтрация по "Названию кабинета". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($room_name) && length($room_name)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from rooms where ROOM_NAME=?";
$sth=$dbh->prepare($sql);
$sth->execute($room_name);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from rooms where ROOM_NAME=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($room_name, $offset, $rows);

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


##################Фильтрация по "Вместимости кабинета". Если данная переменная определена, то осущесвтяется фильтрация, если не определена, то выводится общий список заявок с возможностью поиска
if (defined($capacity_room) && length($capacity_room)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from rooms where CAPACITY_ROOM=?";
$sth=$dbh->prepare($sql);
$sth->execute($capacity_room);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from rooms where CAPACITY_ROOM=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($capacity_room, $offset, $rows);

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

my $sql="select COUNT(*) from rooms where BRANCH=?";
$sth=$dbh->prepare($sql);
$sth->execute($branch);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from rooms where BRANCH=? order by $sort $order limit ?,?";
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

my $sql="select COUNT(*) from rooms";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from rooms order by $sort $order limit ?,?";
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

#Если название кабинета определено, передано и оно не равно 0, то выполняем поиск
if (defined($room) && length($room)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from rooms where ROOM_NAME like ?";
$sth=$dbh->prepare($sql);
$sth->execute('%'.$room.'%');

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;
my $sql1="select * from rooms where ROOM_NAME like ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute('%'.$room.'%', $offset, $rows);

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
else #Иначе название кабинета не определено, не передано и оно равно 0, то показываем весь список кабинетов
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from rooms";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from rooms order by $sort $order limit ?,?";
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