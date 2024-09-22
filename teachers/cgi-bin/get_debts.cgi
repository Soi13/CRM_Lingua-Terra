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
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $teacher_id=$sess->param('teacher_id');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $fio=param('fio');
my $n_dogovor=param('n_dogovor');
$fio=~s/\0//g; $fio=~s/\.\.//g; $fio=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$n_dogovor=~s/\0//g; $n_dogovor=~s/\.\.//g; $n_dogovor=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($fio,'utf8','windows-1251');


if (defined($fio) && length($fio)!=0) #Если ФИО определено, передано и оно не равно 0, то выполняем поиск
{
my @result;
my @res;
my @row_dogovors;
my $cnt=0;
my $res_summ=0;

my $dat;
#Создаем массив из номеров договоров у которых есть график платежей
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select distinct pupils.Num_dogovor from pupils, pays, lessons where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=? and pupils.FIO like ?";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($teacher_id, '%'.$fio.'%');
#В массив записываем извлеченную строку
while ($dat=$sth1->fetchrow_array) {
push @row_dogovors, $dat;
}
################################################

for (my $t=0; $t<=$#row_dogovors; $t++)
{
    #Определяем ФИО студента по его номеру договора
    my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth2=$dbh2->do("SET NAMES 'cp1251'");
    my $sql2="select FIO from pupils where Num_dogovor=?";
    $sth2=$dbh2->prepare($sql2);
    $sth2->execute($row_dogovors[$t]);
    #В массив записываем извлеченную строку
    my @fio = $sth2->fetchrow_array;
    ################################################
    
    #Вычисляем задолженность за предыдущие месяцы по студенту    
    my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth3=$dbh3->do("SET NAMES 'cp1251'");
    my $sql3="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays where concat(SUBSTRING_INDEX(period, '.', -1),SUBSTRING_INDEX(period, '.', 1))<concat(year(now()),month(now())) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";   
    $sth3=$dbh3->prepare($sql3);
    $sth3->execute($row_dogovors[$t]);
    my @row_debt_prev_per = $sth3->fetchrow_array;
    #################################################

    #Вычисляем задолженность за текущий месяц по студенту   
    my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth4=$dbh4->do("SET NAMES 'cp1251'");
    my $sql4="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(month(now()),'.',year(now())) and pupils_num_dogovor=?";
    $sth4=$dbh4->prepare($sql4);
    $sth4->execute($row_dogovors[$t]);
    my @row_debt_present_per = $sth4->fetchrow_array;
    #################################################
    
    #Формируем общую сумму долга студента, на текущий период, для вставки его в массив
    my $common_summ=$row_debt_prev_per[0]+$row_debt_present_per[0];

    #Еслу сумма долга больше 0, то записывыаем ее в массив для вывода в DataGrid
    if ($common_summ>0)
    {
       #Формируем массив для вывода его в Datagrid
       push @result, {"nm_dg"=>$row_dogovors[$t],"fio"=>$fio[0],"summ"=>$common_summ};
       
       $cnt++;
       $res_summ=$res_summ+$common_summ;
    }
    
    
    #Сбрасываем массив каждую итерацию цикла, для помещения
    @fio=();
    @row_debt_present_per=();
    @row_debt_prev_per=();    
    }

my $cgi=CGI->new;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $cnt, footer => [{count=>$res_summ." руб.", name=>"Общая сумма:"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
elsif (defined($n_dogovor) && length($n_dogovor)!=0)
{
my @result;
my @res;
my @row_dogovors;
my $cnt=0;
my $res_summ=0;

my $dat;
#Создаем массив из номеров договоров у которых есть график платежей
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select distinct pupils.Num_dogovor from pupils, pays, lessons where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=? and pupils.Num_dogovor=?";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($teacher_id ,$n_dogovor);
#В массив записываем извлеченную строку
while ($dat=$sth1->fetchrow_array) {
push @row_dogovors, $dat;
}
################################################

for (my $t=0; $t<=$#row_dogovors; $t++)
{
    #Определяем ФИО студента по его номеру договора
    my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth2=$dbh2->do("SET NAMES 'cp1251'");
    my $sql2="select FIO from pupils where Num_dogovor=?";
    $sth2=$dbh2->prepare($sql2);
    $sth2->execute($row_dogovors[$t]);
    #В массив записываем извлеченную строку
    my @fio = $sth2->fetchrow_array;
    ################################################
    
    #Вычисляем задолженность за предыдущие месяцы по студенту    
    my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth3=$dbh3->do("SET NAMES 'cp1251'");
    #my $sql3="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays where SUBSTRING_INDEX(period, '.', 1)<month(now()) and SUBSTRING_INDEX(period, '.', -1)<=year(now()) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";
    my $sql3="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays where concat(SUBSTRING_INDEX(period, '.', -1),SUBSTRING_INDEX(period, '.', 1))<concat(year(now()),month(now())) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";
    $sth3=$dbh3->prepare($sql3);
    $sth3->execute($row_dogovors[$t]);
    my @row_debt_prev_per = $sth3->fetchrow_array;
    #################################################

    #Вычисляем задолженность за текущий месяц по студенту   
    my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth4=$dbh4->do("SET NAMES 'cp1251'");
    my $sql4="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(month(now()),'.',year(now())) and pupils_num_dogovor=?";
    $sth4=$dbh4->prepare($sql4);
    $sth4->execute($row_dogovors[$t]);
    my @row_debt_present_per = $sth4->fetchrow_array;
    #################################################
    
    #Формируем общую сумму долга студента, на текущий период, для вставки его в массив
    my $common_summ=$row_debt_prev_per[0]+$row_debt_present_per[0];

    #Еслу сумма долга больше 0, то записывыаем ее в массив для вывода в DataGrid
    if ($common_summ>0)
    {
       #Формируем массив для вывода его в Datagrid
       push @result, {"nm_dg"=>$row_dogovors[$t],"fio"=>$fio[0],"summ"=>$common_summ};
       
       $cnt++;
       $res_summ=$res_summ+$common_summ;
    }
    
    
    #Сбрасываем массив каждую итерацию цикла, для помещения
    @fio=();
    @row_debt_present_per=();
    @row_debt_prev_per=();    
    }

my $cgi=CGI->new;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $cnt, footer => [{count=>$res_summ." руб.", name=>"Общая сумма:"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
else #Иначе ФИО не определено, не передано и оно равно 0, то показываем весь список студентов
{

my @result;
my @res;
my @row_dogovors;
my $cnt=0;
my $res_summ=0;

my $dat;
#Создаем массив из номеров договоров у которых есть график платежей
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select distinct pays.PUPILS_NUM_DOGOVOR from pays, lessons where pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=?";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($teacher_id);
#В массив записываем извлеченную строку
while ($dat=$sth1->fetchrow_array) {
push @row_dogovors, $dat;
}
################################################

for (my $t=0; $t<=$#row_dogovors; $t++)
{
    #Определяем ФИО студента по его номеру договора
    my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth2=$dbh2->do("SET NAMES 'cp1251'");
    my $sql2="select FIO from pupils where Num_dogovor=?";
    $sth2=$dbh2->prepare($sql2);
    $sth2->execute($row_dogovors[$t]);
    #В массив записываем извлеченную строку
    my @fio = $sth2->fetchrow_array;
    ################################################
    
    #Вычисляем задолженность за предыдущие месяцы по студенту    
    my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth3=$dbh3->do("SET NAMES 'cp1251'");
    my $sql3="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays where concat(SUBSTRING_INDEX(period, '.', -1),SUBSTRING_INDEX(period, '.', 1))<concat(year(now()),month(now())) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";   
    $sth3=$dbh3->prepare($sql3);
    $sth3->execute($row_dogovors[$t]);
    my @row_debt_prev_per = $sth3->fetchrow_array;
    #################################################

    #Вычисляем задолженность за текущий месяц по студенту   
    my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
    my $sth4=$dbh4->do("SET NAMES 'cp1251'");
    my $sql4="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(month(now()),'.',year(now())) and pupils_num_dogovor=?";
    $sth4=$dbh4->prepare($sql4);
    $sth4->execute($row_dogovors[$t]);
    my @row_debt_present_per = $sth4->fetchrow_array;
    #################################################
    
    #Формируем общую сумму долга студента, на текущий период, для вставки его в массив
    my $common_summ=$row_debt_prev_per[0]+$row_debt_present_per[0];

    #Еслу сумма долга больше 0, то записывыаем ее в массив для вывода в DataGrid
    if ($common_summ>0)
    {
       #Формируем массив для вывода его в Datagrid
       push @result, {"nm_dg"=>$row_dogovors[$t],"fio"=>$fio[0],"summ"=>$common_summ};
       
       $cnt++;
       $res_summ=$res_summ+$common_summ;
    }
    
    
    #Сбрасываем массив каждую итерацию цикла, для помещения
    @fio=();
    @row_debt_present_per=();
    @row_debt_prev_per=();    
    }

my $cgi=CGI->new;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $cnt, footer => [{count=>$res_summ." руб.", name=>"Общая сумма:"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}


#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://teachers.linguaterra-soft.ru');
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
else { print "Location: https://teachers.linguaterra-soft.ru\n\n"; }


__END__