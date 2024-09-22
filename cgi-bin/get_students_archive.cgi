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
my $n_dogovor=param('n_dogovor');
$fio=~s/\0//g; $fio=~s/\.\.//g; $fio=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$n_dogovor=~s/\0//g; $n_dogovor=~s/\.\.//g; $n_dogovor=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
my $dt_fil=param('data_filter');
my @data_filter=split(",", $dt_fil);
my $erase_filter=param('erase_filter');
$erase_filter=~s/\0//g; $erase_filter=~s/\.\.//g; $erase_filter=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($fio,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно

foreach my $dt_f (@data_filter)
{
   $dt_f=~s/\0//g;
   $dt_f=~s/\.\.//g;
   $dt_f=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
   Encode::from_to($dt_f,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
}



##################Фильтрация по Удаление фильтра
if (defined($erase_filter))
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from pupils_archive";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from pupils_archive order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################Фильтрация по разным параметрам
if (@data_filter)
{
my @res_filter;

for (my $n=0; $n<=$#data_filter; $n=$n+2)
{
  push @res_filter, $data_filter[$n]."='".$data_filter[$n+1]."' and ";  
}

my $h=$res_filter[$#res_filter];
$h=~s/and//;
$h=~s/\s//;

pop(@res_filter);
push @res_filter, $h;

my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from pupils_archive where @res_filter";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from pupils_archive where @res_filter order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

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

my $sql="select COUNT(*) from pupils_archive where FIO like ?";
$sth=$dbh->prepare($sql);
$sth->execute('%'.$fio.'%');

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from pupils_archive where FIO like ? order by $sort $order limit ?,?";
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
elsif (defined($n_dogovor) && length($n_dogovor)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from pupils_archive where Num_dogovor like ?";
$sth=$dbh->prepare($sql);
$sth->execute($n_dogovor);

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from pupils_archive where Num_dogovor like ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($n_dogovor, $offset, $rows);

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

my $sql="select COUNT(*) from pupils_archive";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from pupils_archive order by $sort $order limit ?,?";
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