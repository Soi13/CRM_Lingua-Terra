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

my $cgi=CGI->new;
my @res;

my $nm_dg=param('data');

#Определяем наименование группы и стоимость курса
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select GROUP_NAME, PRICE_COURSE from groups_students_archive where PUPILS_NUM_DOGOVOR=?";
$sth=$dbh->prepare($sql);
$sth->execute($nm_dg);
my @row_dat = $sth->fetchrow_array;
#################################################

#Вычисляем задолженность за предыдущие месяцы по студенту
my $data1;
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays_archive where SUBSTRING_INDEX(period, '.', 1)<month(now()) and SUBSTRING_INDEX(period, '.', -1)<=year(now()) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($nm_dg);
my @row_debt_prev_per = $sth1->fetchrow_array;
#################################################

#Вычисляем задолженность за текущий месяц по студенту
my $data2;
my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select summ_4_opl - opl_summ as RES from pays_archive where period=CONCAT(month(now()),'.',year(now())) and pupils_num_dogovor=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($nm_dg);
my @row_debt_present_per = $sth2->fetchrow_array;
#################################################

#Вычисляем оплаченную суммы за предыдущие и текущий периоды (всего оплачено по текущему курсу/группе) 
my $data3;
my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
my $sql3="select SUM(opl_summ) as RES from pays_archive where pupils_num_dogovor=? and (opl_summ is not NULL and opl_summ >0)";
$sth3=$dbh3->prepare($sql3);
$sth3->execute($nm_dg);
my @row_paid = $sth3->fetchrow_array;
#################################################

#Формируем общую сумму долга студента, на текущий период, для вывода в окно создания платежа
my $common_summ=$row_debt_prev_per[0]+$row_debt_present_per[0];

#Формируем общую сумму долга студента за весь курс
my $common_summ_debt=$row_dat[1]-$row_paid[0];


#Подсчитываем процент оплаты студентом полной стоимости курса
my $proc_stud=int($row_paid[0]*100/$row_dat[1]);

if (@row_dat)
{
  my $op=JSON->new->pretty(1);
  #my $json=$op->encode(@res);
  my $json=$op->encode({result => $row_dat[0]." - ".$row_dat[1]." руб.", proc => $proc_stud, summ_debt => $common_summ_debt, summ_debt_curr_per => $common_summ});

  print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
  print $json;
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