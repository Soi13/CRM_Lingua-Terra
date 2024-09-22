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

my $offset=($page-1)*$rows;

#Удаляем просроченные сессии из БД, для отображения только активных сессий пользователй
CGI::Session->find("driver:mysql", \&del_old_ses, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from sessions";
$sth=$dbh->prepare($sql);
$sth->execute();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

my $sql1="select * from sessions order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}
$dbh->disconnect;

#Ниже идет функционал по извлечению логина пользовтеля из строки сессии и подстановка (замена вместо полной строки сессии) его в массив для вывода этой инфы на странице
my $login;
for (my $k==0; $k<=$#result; $k++) # Бежим циклом по массиву и читаем колонку с внутренностями сессии
{
   my $st=$result[$k]->{"a_session"};
   $st=~/\{(.+)\}/is; #Получаем содержимое инфы в фигурных скобках
   my $rr_st=$1;
   $rr_st=~s/\s//isg; #Удаляем пробелы
   $rr_st=~s/=>/,/isg; #Меняем => на ,
   $rr_st=~s/'//isg; #Удаляем '
   my @arr_st=split(/,/, $rr_st); 
   for(my $d==0; $d<=$#arr_st; $d++) #В цикле ишем элемент массива с текстом Login и читаем следующий за ним элемент - это и есть логин пользователя.
   {
     if ($arr_st[$d] eq "Login")
     {
       $login=$arr_st[$d+1];
       last;
     }
   }
  
   $result[$k]->{"a_session"}=$login;
   $login=""; #Очищаем логин
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();



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

#Функция удаления просроченных сессий
sub del_old_ses {
	my ($session)=@_;
	next if $session->is_empty();
	if (($session->ctime()+86400)<time()) {
	$session->delete();
	}

}

}
else { print "Location: http://localhost:6080\n\n"; }


__END__