#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI qw(:cgi);
use Encode;
use LWP::UserAgent; 
use Time::Local; 
use Digest::MD5 qw(md5_hex);

my $lg=param('lg');
my $psw=param('psw');
$lg=~s/\0//g; $lg=~s/\.\.//g; $lg=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$psw=~s/\0//g; $psw=~s/\.\.//g; $psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

$psw=md5_hex($psw);

if ($lg eq "Sender_SMS" && $psw eq "d6395bcbddbc4d3c19234a2f32947dc3")
{
my $prih_ord="Приходный ордер";
my $status="Наличные";
Encode::from_to($prih_ord,'utf8','windows-1251');
Encode::from_to($status,'utf8','windows-1251');

#Получаем сумму, которую оплатили наличкой студенты за текущий день в Кемерово
my $dbh2=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016") or die "Error: $DBI::errstr\n";
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select sum(orders.SUMM_OPL) from orders, pupils where orders.PUPILS_NUM_DOGOVOR_OR_KA=pupils.Num_dogovor and pupils.BRANCH not in (6,12) and concat(year(orders.DATETIME_CREATE),month(orders.DATETIME_CREATE),day(orders.DATETIME_CREATE))=concat(year(NOW()),month(NOW()),day(NOW())) and orders.TYPE_DOC=? and orders.STATUS=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($prih_ord, $status);
#В массив записываем извлеченную строку
my @row_sum_kemerovo = $sth2->fetchrow_array;

my $sum_kemerovo=0;
if (defined($row_sum_kemerovo[0]))
{
  $sum_kemerovo=$row_sum_kemerovo[0];
}

#Получаем сумму, которую оплатили наличкой студенты за текущий день в Ленинск-Кузнецке
my $dbh3=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016") or die "Error: $DBI::errstr\n";
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
#my $sql3="select sum(SUMM_OPL) from orders where concat(year(DATETIME_CREATE),month(DATETIME_CREATE),day(DATETIME_CREATE))=concat(year(NOW()),month(NOW()),day(NOW())) and TYPE_DOC=? and STATUS=?";
my $sql3="select sum(orders.SUMM_OPL) from orders, pupils where orders.PUPILS_NUM_DOGOVOR_OR_KA=pupils.Num_dogovor and pupils.BRANCH=12 and concat(year(orders.DATETIME_CREATE),month(orders.DATETIME_CREATE),day(orders.DATETIME_CREATE))=concat(year(NOW()),month(NOW()),day(NOW())) and orders.TYPE_DOC=? and orders.STATUS=?";
$sth3=$dbh3->prepare($sql3);
$sth3->execute($prih_ord, $status);
#В массив записываем извлеченную строку
my @row_sum_leninsk = $sth3->fetchrow_array;

my $sum_leninsk=0;
if (defined($row_sum_leninsk[0]))
{
  $sum_leninsk=$row_sum_leninsk[0];
}

#Получаем сумму, которую оплатили наличкой студенты за текущий день в Белово
#my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $dbh4=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016") or die "Error: $DBI::errstr\n";
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
#my $sql4="select sum(SUMM_OPL) from orders where concat(year(DATETIME_CREATE),month(DATETIME_CREATE),day(DATETIME_CREATE))=concat(year(NOW()),month(NOW()),day(NOW())) and TYPE_DOC=? and STATUS=?";
my $sql4="select sum(orders.SUMM_OPL) from orders, pupils where orders.PUPILS_NUM_DOGOVOR_OR_KA=pupils.Num_dogovor and pupils.BRANCH=6 and concat(year(orders.DATETIME_CREATE),month(orders.DATETIME_CREATE),day(orders.DATETIME_CREATE))=concat(year(NOW()),month(NOW()),day(NOW())) and orders.TYPE_DOC=? and orders.STATUS=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($prih_ord, $status);
#В массив записываем извлеченную строку
my @row_sum_belovo = $sth4->fetchrow_array;

my $sum_belovo=0;
if (defined($row_sum_belovo[0]))
{
  $sum_belovo=$row_sum_belovo[0];
}


#Получаем итоговую сумму по всем филиалам
my $itog_sum=$sum_kemerovo+$sum_belovo+$sum_leninsk;

#Если сумма общая сумма равна 0, то скрипт не отправляем для экономии денег
if ($itog_sum==0)
{
  print "Content-type: text/html\n\n";
  print "<html><h1>Stop because of 0 summ</h1></html>\n";
  exit;
}

#Отправляем эту сумму по смс
my $ua = new LWP::UserAgent;
 
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
$year+=1900;
$mon++;

my $login = 'skvortsov@lingua-terra.ru';
my $password = '!Lingua2017#!';
 
my $send_sms = '<?xml version="1.0" encoding="UTF-8"?>    
    <SMS> 
    <operations>  
    <operation>SEND</operation> 
    </operations> 
    <authentification>    
    <username>'.$login.'</username> 
    <password>'.$password.'</password>  
    </authentification>   
    <message> 
    <sender>LinguaTerra</sender>    
    <text>Сумма поступления налички на '.$mday.".".$mon.".".$year.' составила:'. $itog_sum .' руб. Из них: Кемерово: '.$sum_kemerovo.' руб., Белово: '.$sum_belovo.' руб., Ленинск-куз: '.$sum_leninsk.' руб.</text>
    </message>    
    <numbers> 
    <number messageID="msg_pay'.$mday.$mon.$year.'">14086675393</number>  
	</numbers>    
    </SMS>';  
         
my $response = $ua->post('http://api.myatompark.com/members/sms/xml.php',{ XML => $send_sms});
 
#print $response->content; 

print "Content-type: text/html\n\n";
print "<html><h1>Finished</h1></html>\n";
exit;
}
else
{
  print "Content-type: text/html\n\n";
  print "<html><h1>Prohibited!</h1></html>\n";
  exit;
}
__END__