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

my $cgi = CGI->new;
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

my $month=param('month');
my $year=param('year');
my $teacher=param('teacher');
my $individual=param('individual');

$month=~s/\0//g; $month=~s/\.\.//g; $month=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$year=~s/\0//g; $year=~s/\.\.//g; $year=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$teacher=~s/\0//g; $teacher=~s/\.\.//g; $teacher=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$individual=~s/\0//g; $individual=~s/\.\.//g; $individual=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Если препод не выбран, то выводим долг за выбранную дату по всем преподам
if (length($teacher)==0)
{
  my @result;
  my @res;
  my @row_dogovors;
  my $cnt=0;
  my $res_summ=0;
  
  my $sql1;

  if($individual eq "true")
  {
    $sql1="select distinct pays.pupils_num_dogovor from pays, pupils where pays.pupils_num_dogovor=pupils.Num_dogovor and (pupils.individual IS NULL or pupils.individual<>1) order by pays.pupils_num_dogovor";
  }
  else
  {
    $sql1="select distinct pupils_num_dogovor from pays order by pupils_num_dogovor";
  }

  my $dat;
  #Создаем массив из номеров договоров у которых есть график платежей
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  #my $sql1="select distinct pupils_num_dogovor from pays order by pupils_num_dogovor";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
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
    
      #Вычисляем задолженность за выбранный месяц по студенту   
      my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
      my $sth4=$dbh4->do("SET NAMES 'cp1251'");
      my $sql4="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(?,'.',?) and pupils_num_dogovor=?";
      $sth4=$dbh4->prepare($sql4);
      $sth4->execute($month, $year, $row_dogovors[$t]);
      my @row_debt = $sth4->fetchrow_array;
      #################################################
    
      #Формируем общую сумму долга студента, на текущий период, для вставки его в массив
      my $common_summ=$row_debt[0];

      #Еслу сумма долга больше 0, то записывыаем ее в массив для вывода в DataGrid
      if ($common_summ>0)
      {
         #Формируем массив для вывода его в Datagrid
         push @result, {"nm_dg"=>$row_dogovors[$t],"fio"=>$fio[0],"summ"=>$common_summ};
       
         $cnt++;
         $res_summ=$res_summ+$common_summ;
      }
    
    
      #Сбрасываем массив каждую итерацию цикла
      @fio=();
      @row_debt=();
      }

  my $cgi=CGI->new;
  my $op=JSON::XS->new->pretty(1);
  my $json=$op->encode({ rows=> \@result, total => $cnt, footer => [{count=>$res_summ." руб.", name=>"Общая сумма:"}]}  );

  print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

  print $json;
  exit();
}
else #Иначе препод выбран и показываем всех должников за выбранный период по выбранному преподу
{
  my @result;
  my @res;
  my @row_dogovors;
  my $cnt=0;
  my $res_summ=0;
  
  my $sql1;

  if($individual eq "true")
  {
    $sql1="select distinct pays.PUPILS_NUM_DOGOVOR from pays, lessons, pupils where pays.pupils_num_dogovor=pupils.Num_dogovor and pays.GROUP_ID=lessons.GROUP_ID and (pupils.individual IS NULL or pupils.individual<>1) and lessons.TEACHER_ID=? order by pays.PUPILS_NUM_DOGOVOR";
  }
  else
  {
    $sql1="select distinct pays.PUPILS_NUM_DOGOVOR from pays, lessons where pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=? order by pays.PUPILS_NUM_DOGOVOR";
  }

  my $dat;
  #Создаем массив из номеров договоров у которых есть график платежей
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  #my $sql1="select distinct pays.PUPILS_NUM_DOGOVOR from pays, lessons where pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=? order by pays.PUPILS_NUM_DOGOVOR";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute($teacher);
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
    
      #Вычисляем задолженность за текущий месяц по студенту   
      my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
      my $sth4=$dbh4->do("SET NAMES 'cp1251'");
      my $sql4="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(?,'.',?) and pupils_num_dogovor=?";
      $sth4=$dbh4->prepare($sql4);
      $sth4->execute($month, $year, $row_dogovors[$t]);
      my @row_debt = $sth4->fetchrow_array;
      #################################################
    
      #Формируем общую сумму долга студента, на текущий период, для вставки его в массив
      my $common_summ=$row_debt[0];

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
      @row_debt=();
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