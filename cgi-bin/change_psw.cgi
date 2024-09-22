#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use ConnectDB;
use JSON;
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

######Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass))
{

my $curr_psw=$cgi->param('curr_psw');
my $new_psw=$cgi->param('new_psw');
my $new_psw1=$cgi->param('new_psw1');

$curr_psw=~s/\0//g; $curr_psw=~s/\.\.//g; $curr_psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$new_psw=~s/\0//g; $new_psw=~s/\.\.//g; $new_psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$new_psw1=~s/\0//g; $new_psw1=~s/\.\.//g; $new_psw1=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Шифруем пароль
$curr_psw=md5_hex($curr_psw);

#Проверка на существование пользователя в БД по введенному паролю и логину
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select * from usr where LOGIN like ? and PASSW like ?";
$sth=$dbh->prepare($sql);
$sth->execute($formLogin,$curr_psw);

#Получаем кол-во строк
my $rows_affected = $sth->rows();

#В массив записываем извлеченную строку
my @row = $sth->fetchrow_array;

$dbh->disconnect;

#########Если выбрано строк 0, то пароль или логин были не верными
if ($rows_affected==0)
{
    my $ans="Текущий пароль задан не верно!";
    #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit();
}
###################################################################


#######Если новые пароли не совпадают, уведомляем пользователя.
if ($new_psw ne $new_psw1)
{
  my $ans="Введенные пароли не совпадают!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

#######Если новый пароль совпадает с предыдущим, то уведомляем пользователя и блокируем изменение.
if ((md5_hex($new_psw) eq $curr_psw) && (md5_hex($new_psw1) eq $curr_psw))
{
  my $ans="Введенный пароль совпадает с предыдущим. Изменение невозможно!";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################


######Если пароль не отвечает правилу сложности, то выводим сообщение пользователю
if (($new_psw!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm) && ($new_psw1!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm))
{
  my $ans="Введенный пароль не соответствует требованиям сложности! Пароль должен иметь длинну от 8 до 20 символов, содержать хотя бы одну цифру, одну букву заглавную и прописную, а также содержать один из символов (@#\$%!).";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################


###########Проверяем совпадают ли введенный пароль с логином и паролем полученными после запроса, и если совпадают, то делаем UPDATE пароля
if ($row[1] eq $formLogin && $row[2] eq $curr_psw)
{
  #Проверка кол-ва старых паролей. Если записей менее 5, то добавляем старый пароль в таблицу old_passw, если больше 5, то делаем update на записи таблице с наименьшей датой создания
  my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="select USER_ID from old_passw where USER_ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($row[0]);
  #Получаем кол-во строк
  my $rows_count = $sth2->rows();
  
  if ($rows_count<5) 
  {
     #Проверка вводимого пользователем пароля. Если пароль есть среди последних 5-ти вводимых, то его ввод запрещен!
     my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
     my $sth2=$dbh2->do("SET NAMES 'cp1251'");
     my $sql2="select PASSW from old_passw where USER_ID=? and PASSW=?";
     $sth2=$dbh2->prepare($sql2);
     $sth2->execute($row[0], md5_hex($new_psw));
     #В массив записываем извлеченную строку
     my @row_psw = $sth2->fetchrow_array;
     
     if (@row_psw)
     {
             my $ans="Вводимый пароль присутствует в списке 5 предыдущих паролей. Введите другой пароль!";
             #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
     else
     {     
             
             #Вставляем в таблицу old_passw текущий пароль, перед заменой его на новый
             my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
             my $sth3=$dbh3->do("SET NAMES 'cp1251'");
             my $sql3="insert into old_passw (USER_ID, PASSW, DATETIME_CREATE) values (?,?, NOW())";
             $sth3=$dbh3->prepare($sql3); #Для операций которые не возвращают значение
             $sth3->execute($row[0], $curr_psw);
             $dbh3->disconnect;
             
             #Меняем пароль
             my $md5_psw=md5_hex($new_psw); # Шифруем пароль
             my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
             my $sth1=$dbh1->do("SET NAMES 'cp1251'");
             my $sql1="update usr set PASSW=?, PASSW_DATE_EXPIRED=ADDDATE(NOW(), ?) where ID like ?";
             $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
             $sth1->execute($md5_psw, $row[63], $row[0]);
             $dbh1->disconnect;

             my $ans="Пароль заменен успешно!";
             #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
  }
  
  
  if ($rows_count==5)
  {
     #Проверка вводимого пользователем пароля. Если пароль есть среди последних 5-ти вводимых, то его ввод запрещен!
     my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
     my $sth2=$dbh2->do("SET NAMES 'cp1251'");
     my $sql2="select PASSW from old_passw where USER_ID=? and PASSW=?";
     $sth2=$dbh2->prepare($sql2);
     $sth2->execute($row[0], md5_hex($new_psw));
     #В массив записываем извлеченную строку
     my @row_psw = $sth2->fetchrow_array;
     
     if (@row_psw)
     {
             my $ans="Вводимый пароль присутствует в списке 5 предыдущих паролей. Введите другой пароль!";
             #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
     else
     {     
             #Определение наиболее старой записи в старых паролях студента, для ее update
             my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
             my $sth4=$dbh4->do("SET NAMES 'cp1251'");
             my $sql4="select min(DATETIME_CREATE) as dt_cr from old_passw where USER_ID=?";
             $sth4=$dbh4->prepare($sql4);
             $sth4->execute($row[0]);
             #В массив записываем извлеченную строку
             my @row_old_psw = $sth4->fetchrow_array;
            
            
             #Update в таблице old_passw запись с паролем с наименьшей датой
             my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
             my $sth3=$dbh3->do("SET NAMES 'cp1251'");
             my $sql3="update old_passw set PASSW=?, DATETIME_CREATE=NOW() where USER_ID=? and DATETIME_CREATE=?";
             $sth3=$dbh3->prepare($sql3); #Для операций которые не возвращают значение
             $sth3->execute($curr_psw, $row[0], $row_old_psw[0]);
             $dbh3->disconnect;
             
             #Меняем пароль
             my $md5_psw=md5_hex($new_psw); # Шифруем пароль
             my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
             my $sth1=$dbh1->do("SET NAMES 'cp1251'");
             my $sql1="update usr set PASSW=?, PASSW_DATE_EXPIRED=ADDDATE(NOW(), ?) where ID like ?";
             $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
             $sth1->execute($md5_psw, $row[63], $row[0]);
             $dbh1->disconnect;

             my $ans="Пароль заменен успешно!";
             #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
             my $res=$ans;

             #convert  data to JSON
             my $op = JSON -> new -> pretty(1);
             my $json = $op -> encode({result => $res});

             print $cgi->header('application/json;charset=windows-1251');
             print $json;
             exit();
     }
  }

}
##############################################################

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################



