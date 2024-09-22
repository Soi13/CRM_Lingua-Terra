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
my $us_id=$sess->param('USER_ID');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $nm_dg=param('num_dg');
$nm_dg=~s/\0//g; $nm_dg=~s/\.\.//g; $nm_dg=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Проверяем привязан ли студент к группе. Если да, то еще одна привязка не возможна, т.к. одновремиенно находится в друг группах один и тот же студент не может. Необходимо создать еще доп.договор для этого студента.
my $dbh7=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth7=$dbh7->do("SET NAMES 'cp1251'");
my $sql7="select PUPILS_NUM_DOGOVOR from groups_students where PUPILS_NUM_DOGOVOR=?";
$sth7=$dbh7->prepare($sql7);
$sth7->execute($nm_dg);
#В массив записываем извлеченную строку
my @stud = $sth7->fetchrow_array;
if (!@stud)
{
    my$ans="Студент не привязан ни к одной группе. Перенос оплат не возможен!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    ############################################################  
    
    exit;      
}

#Получаем данные по безгрупповым оплатам студента,чтобы потом их вставить в основной раздел оплат
my $data_pays;
my @rows_data_pays;
my $dbh_wp=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_wp=$dbh_wp->do("SET NAMES 'cp1251'");
my $sql_wp="select OPL_SUMM, DATE_OF_PAY, STATUS, NOTES from pays_without_group where PUPILS_NUM_DOGOVOR=?";
$sth_wp=$dbh_wp->prepare($sql_wp);
$sth_wp->execute($nm_dg);
#В массив записываем извлеченные строки
while ($data_pays=$sth_wp->fetchrow_hashref) {
push  @rows_data_pays, $data_pays;
} 
############################

########Проверка на наличие суммы платежа
for (my $z=0; $z<=$#rows_data_pays; $z++)
{
  if ((length($rows_data_pays[$z]->{"OPL_SUMM"})==0) || ($rows_data_pays[$z]->{"OPL_SUMM"}=='0'))
  {
    my $ans="Одна или более из переносимых оплат не заполнена!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json; 
    exit;
  }           
}


########Проверка на корректность суммы платежа
#for (my $z1=0; $z1<=$#rows_data_pays; $z1++)
#{
#  if ($rows_data_pays[$z1]->{"OPL_SUMM"}!~m/^\s*\d+\.\d+\s*$/is)
#  {
#    my $ans="Одна или более из сумм переносимых оплат не корректна. Формат должен быть, например, 2000.00";
#    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
#    my $res=$ans;

#    #convert  data to JSON
#    my $op = JSON -> new -> pretty(1);
#    my $json = $op -> encode({result => $res});

#    print $cgi->header('application/json;charset=windows-1251');
#    print $json; 
#    exit;
#  }           
#}


########Проверка на наличие даты платежа
for (my $z2=0; $z2<=$#rows_data_pays; $z2++)
{
  if (length($rows_data_pays[$z2]->{"DATE_OF_PAY"})==0)
  {
    my $ans="Одна или более из переносимых оплат не содержит дату оплаты.";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json; 
    exit;
  }           
}


#Проверка корректности даты платежа
for (my $z3=0; $z3<=$#rows_data_pays; $z3++)
{
  if ($rows_data_pays[$z3]->{"DATE_OF_PAY"}!~m/(^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$/is)
  {
    my $ans="Одна или более из переносимых оплат имеет неверный формат даты. Формат должен быть, например, 2016-05-30.";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json; 
    exit;
  }           
}


#Проверка на ввод вида оплаты
for (my $z4=0; $z4<=$#rows_data_pays; $z4++)
{
  if (length($rows_data_pays[$z4]->{"STATUS"})==0)
  {
    my $ans="У одной или более из переносимых оплат не указан вид оплаты.";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json; 
    exit;
  }           
}



#Производим перенос безгрупповых платежей
for (my $z5=0; $z5<=$#rows_data_pays; $z5++)
{
  my @row;
  my @data;
  my $cgi=CGI->new;

  #Определяем язык, вид программы и наименование группы студента
  my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth4=$dbh4->do("SET NAMES 'cp1251'");
  my $sql4="select kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, groups.GROUP_NAME from kind_languages, kind_programm,groups, groups_students where kind_languages.ID=groups.LANGUAGE and kind_programm.ID=groups.KIND_PROGRAMM and groups.ID=groups_students.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
  $sth4=$dbh4->prepare($sql4);
  $sth4->execute($nm_dg);
  my @data_stud = $sth4->fetchrow_array;
   

  #Выбираем записи/периоды по студенту которые полностью не оплачены, либо оплачено не полностью
  my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  my $sql="select pupils_num_dogovor, period, summ_4_opl, opl_summ from pays where pupils_num_dogovor=? and (opl_summ=0 or summ_4_opl>opl_summ) order by (SUBSTRING_INDEX(period, '.', -1)+0), (SUBSTRING_INDEX(period, '.', 1)+0)";
  $sth=$dbh->prepare($sql);
  $sth->execute($nm_dg);

  #Записываем все в массив
  while (@data=$sth->fetchrow_array) {
  push @row, @data;
  }

  my $input_summ=$rows_data_pays[$z5]->{"OPL_SUMM"};
  my $common_sum;

  for (my $p=0; $p<=$#row; $p=$p+4)
  {
      $common_sum=$common_sum+($row[$p+2]-$row[$p+3]);        
  }

  if ($input_summ>$common_sum)
  {
     my $ans="Вносимая оплата больше, чем осталось оплатить по данному курсу. Остаток за курс ".$common_sum." руб., а вы вносите ".$input_summ." руб."; 
     #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
     my $res=$ans;

     #convert  data to JSON
     my $op = JSON -> new -> pretty(1);
     my $json = $op -> encode({result => $res});

     print $cgi->header('application/json;charset=windows-1251');
     print $json; 
    exit;
  }


  #Обрабатываем массив и разносим сумму по неоплаченным или недоплаченным периодам
  for (my $i=0; $i<=$#row; $i=$i+4)
  {
     my $diff_sum=$row[$i+2]-$row[$i+3];
     
     if ($input_summ<$diff_sum)
     {         
        my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update pays set OPL_SUMM=OPL_SUMM+?, DATE_OF_PAY=?, STATUS=?, NOTES=? where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
        $sth2=$dbh2->prepare($sql2);   
        $sth2->execute($input_summ, $rows_data_pays[$z5]->{"DATE_OF_PAY"}, $rows_data_pays[$z5]->{"STATUS"}, $rows_data_pays[$z5]->{"NOTES"}, $row[$i], $row[$i+1]);
        last;
     }
     
     $input_summ-=$diff_sum;
     
     my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
     my $sth1=$dbh1->do("SET NAMES 'cp1251'");
     my $sql1="update pays set OPL_SUMM=?, DATE_OF_PAY=?, STATUS=?, NOTES=? where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
     $sth1=$dbh1->prepare($sql1);
     $sth1->execute($row[$i+2], $rows_data_pays[$z5]->{"DATE_OF_PAY"}, $rows_data_pays[$z5]->{"STATUS"}, $rows_data_pays[$z5]->{"NOTES"}, $row[$i], $row[$i+1]); 
     
     if ($input_summ<$row[$i+2])
     {         
        my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update pays set OPL_SUMM=?, DATE_OF_PAY=?, STATUS=?, NOTES=? where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
        $sth2=$dbh2->prepare($sql2);   
        $sth2->execute($input_summ, $rows_data_pays[$z5]->{"DATE_OF_PAY"}, $rows_data_pays[$z5]->{"STATUS"}, $rows_data_pays[$z5]->{"NOTES"}, $row[$i], $row[$i+5]);
        last;
     }     
  }

  #Генерируем приходный ордер по совершенному платежу
  my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="insert into orders (TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, USER_ID, DATETIME_CREATE, STATUS) values ('Приходный ордер',?,?,?,?,?,NOW(),?)";
  $sth3=$dbh3->prepare($sql3);   
  $sth3->execute($rows_data_pays[$z5]->{"DATE_OF_PAY"}, $nm_dg, "Обучение. Язык: ".$data_stud[0]." Программа: ".$data_stud[1], $rows_data_pays[$z5]->{"OPL_SUMM"}, $us_id, $rows_data_pays[$z5]->{"STATUS"});

}

my $dbh5=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth5=$dbh5->do("SET NAMES 'cp1251'");
my $sql5="delete from pays_without_group where pupils_num_dogovor=?";
$sth5=$dbh5->prepare($sql5);
$sth5->execute($nm_dg);

my $dbh6=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth6=$dbh6->do("SET NAMES 'cp1251'");
my $sql6="delete from orders_without_group where pupils_num_dogovor_or_ka=?";
$sth6=$dbh6->prepare($sql6);
$sth6->execute($nm_dg);

$dbh5->disconnect; 
$dbh6->disconnect; 

my $ans="Оплаты перенесены успешно!"; 
#Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
############################################################

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
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