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

my $nm_dg=param('num_dg_stud_without_gr');
my $sum_pay=param('SUM_PAY_WITHOUT_GR');
my $notes=param('NOTES_PAY_WITHOUT_GR');
my $date_pay=param('DATE_PAY_WITHOUT_GR');
my $kind_opl=param('KIND_OPL_WITHOUT_GR');
my $osnovanie_opl=param('OSNOVANIE_OPL');
$nm_dg=~s/\0//g; $nm_dg=~s/\.\.//g; $nm_dg=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$sum_pay=~s/\0//g; $sum_pay=~s/\.\.//g; $sum_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$notes=~s/\0//g; $notes=~s/\.\.//g; $notes=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$date_pay=~s/\0//g; $date_pay=~s/\.\.//g; $date_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$kind_opl=~s/\0//g; $kind_opl=~s/\.\.//g; $kind_opl=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$osnovanie_opl=~s/\0//g; $osnovanie_opl=~s/\.\.//g; $osnovanie_opl=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($notes,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($kind_opl ,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
Encode::from_to($osnovanie_opl ,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно


#Проверяем привязан ли студент к группе. Если да, то вводить оплаты в раздел безгрупповые оплаты нельзя, вночить можно в основные оплаты.
my $dbh5=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth5=$dbh5->do("SET NAMES 'cp1251'");
my $sql5="select PUPILS_NUM_DOGOVOR from groups_students where PUPILS_NUM_DOGOVOR=?";
$sth5=$dbh5->prepare($sql5);
$sth5->execute($nm_dg);
#В массив записываем извлеченную строку
my @stud = $sth5->fetchrow_array;
if (@stud)
{
   my$ans="Студент привязан к группе. В таком случае ввод оплат необходимо производить в основном разделе по вводу оплат, закладка \"Платежи\"";
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

########Проверка на ввод суммы платежа
if ((length($sum_pay)==0) ||($sum_pay=='0.00'))
{
  my $ans="Необходимо заполнить сумму платежа!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на корректность суммы платежа
if ($sum_pay!~m/^\s*\d+\.\d+\s*$/is)
{
        my $ans="Введенная сумма платежа не корректна. Формат должен быть, например, 2000.00";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
##############################################################

########Проверка на ввод даты платежа
if (length($date_pay)==0)
{
  my $ans="Необходимо заполнить дату платежа!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

#Проверка корректности даты платежа
## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
if ($date_pay!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="Введенная дата платежа не корректна. Формат должен быть, например, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
###########################################################################################################################################
# Разбираем дату на день месяу и год и проверяем чтобы части даты не превышали дозволенные. Например месяц не может быть больше 12, день 31
###########################################################################################################################################
        
# Извлекаем месяц и проверяем. После отработки регулярки в переменную $& записывается результат. 
$date_pay=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="В введенной дате платежа не корректен месяц. Месяц не может быть больше 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем год и проверяем. После отработки регулярки в переменную $& записывается результат. 
$date_pay=~/\d{4}/;
if ($&>3000)
{
        my $ans="В введенной дате платежа не разумно большой год.";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# Извлекаем дату и проверяем. После отработки регулярки в переменную $& записывается результат. 
$date_pay=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="В введенной дате платежа не корректно задано число! Число не может быть более 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########Проверка на ввод вида оплаты
if (length($kind_opl)==0)
{
  my $ans="Необходимо заполнить вид оплаты!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########Проверка на ввод Только корректных Видов оплат
my $dbh_opl=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_opl=$dbh_opl->do("SET NAMES 'cp1251'");

my $sql_opl="select KIND_OPLATA from kind_pay where KIND_OPLATA=?"; 
$sth_opl=$dbh_opl->prepare($sql_opl);
$sth_opl->execute($kind_opl);
my $cnt=$sth_opl->rows();
$dbh_opl->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Вид оплаты\" должно содержать только данные из списка!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################


my $cgi=CGI->new;

#Добавляем оплату студенту
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="insert into pays_without_group (PUPILS_NUM_DOGOVOR, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,NOW())";
$sth=$dbh->prepare($sql);   
$sth->execute($nm_dg, $sum_pay, $date_pay, $kind_opl, $notes, $us_id);

#Генерируем приходный ордер по совершенному платежу
my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
my $sql3="insert into orders_without_group (TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, USER_ID, DATETIME_CREATE, STATUS) values ('Приходный ордер',?,?,?,?,?,NOW(),?)";
$sth3=$dbh3->prepare($sql3);   
$sth3->execute($date_pay, $nm_dg, $osnovanie_opl, $sum_pay, $us_id, $kind_opl);


$dbh->disconnect;
$dbh3->disconnect;

my $ans="Оплата принята успешно!"; 
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