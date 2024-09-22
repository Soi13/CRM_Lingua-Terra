#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Time::Local;
use Digest::MD5 qw(md5_hex);
use Lingua::Translit;

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
my $us_id=$sess->param('USER_ID');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

#Создаем массив полей переданных из формы
my $idd=param('id_x1');  
$idd=~s/\0//g; $idd=~s/\.\.//g; $idd=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

  ################################### По ID определяем заявку и извлекаем все поля и записываем их в массив   @row_zayav для вставки их в таблицу pupils
  my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  my $sql="select * from zayavki where ID=?";
  $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
  $sth->execute($idd);
  #В массив записываем извлеченную строку
  my @row_zayav = $sth->fetchrow_array;  
  $dbh->disconnect;
  ################################################
  

  ###################################Генерируем UUID для вставки его в таблицу pupils. По этому полю в дальнейшем мы сможем определить номер договора созданного студента и по номеру привязать запись в таблице history_students
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #В массив записываем извлеченную строку
  my @row_uuid = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################
  
  #####Генерируем пароль для студента путем транслитерации его фамилии и подстановки текущего года и нескольких знаков
  #Определяем текущий год
  (my $sec,my $min,my $hour,my $mday,my $mon,my $year,my $wday,my $pointer,my $pointer) = localtime(time);
  $year+=1900;
  
  #Производим непосредственно транслитерацию
  my $full_name=$row_zayav[4];
  my @surname=split(' ', $full_name);
  Encode::from_to($surname[0],'windows-1251','utf8'); 
  my $str = $surname[0];
  my $tr = new Lingua::Translit("GOST 7.79 RUS");
  my $result;
  if ($tr->can_reverse()) {
    $result = $tr->translit($str);
  }
 
  $result=~s/\'//;
  $result=~s/\`//; 
  my $result_psw_cl=$result.$year."!#%";
  my $result_md5=md5_hex($result.$year."!#%");  
  ###################################################

  ###################################Вставляем данные из заявки в таблицу pupils, затем в history_students и только затем удаляем заявку из таблицы zayavki
  #Используем метод транзакций и блок Eval с переменной $@, если произошла ошибка во время выполнения SQL команд в блоке Eval, то выполняем откат операций
  #my $txt="Заявка получена ".$row_zayav[1]."; Заявку принял: ".$row_zayav[2]."; Желаемый язык: ".$row_zayav[7]."; Дата и время тестирования: ".$row_zayav[12]." ".$row_zayav[13];
  
  my $dbh2=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  eval {  
  #Вставляем/переносим данные из заявки в таблицу pupils
  my $sql2="insert into pupils (FIO, FIO_PARENT, BRANCH, MOBILE_PHONE, SOURCE_ABOUT_US, USER_ID, GUID, MARK_FROM_ZAYAV, DATE_OF_BORN, DATE_OF_FILLING, PASSW, TEMP_PASSW) values (?,?,?,?,?,?,?,?,?, NOW(),?,?)";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($row_zayav[4], $row_zayav[5], $row_zayav[9], $row_zayav[10], $row_zayav[11], $us_id, $row_uuid[0],1, $row_zayav[17], $result_md5, $result_psw_cl);
  
  #Определяем номер договора вставленного/перенесенного студента из заявки в pupils по GUID
  $sql2="select Num_dogovor from pupils where GUID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($row_uuid[0]);
  #В массив записываем извлеченный номер договора
  my @num_dog = $sth2->fetchrow_array; 
  
  #Вставка данных о заявке в историю студента
  #$sql2="insert into history_students (PUPILS_NUM_DOGOVOR, TEXT, DATETIME_CREATE, USER_ID) values (?,?,NOW(),?)";
  $sql2="insert into history_students (PUPILS_NUM_DOGOVOR, TEXT, DATETIME_CREATE, USER_ID) values (?,CONCAT('Заявку получена:',?,    ' Заявку принял:',(select FIO from users_get_zayav where ID=?),    ' Желаемый язык: ',(select LANGUAGE from kind_languages where ID=?),    ' Дата и время тестирования:',?,' ',?,     'Уровень владения: ',(select LEVEL from level_knowledge where ID=?)         ),NOW(),?)";  
  $sth2=$dbh2->prepare($sql2);
  #$sth2->execute($num_dog[0], $txt, $us_id);
  $sth2->execute($num_dog[0], $row_zayav[1], $row_zayav[2], $row_zayav[7], $row_zayav[12], $row_zayav[13], $row_zayav[8], $us_id);  

  #Вставка номера договора студента появивщегося путем переноса заявки в поле PUPIL_NUM_DOGOVOR в календарь в таблицу calendar_events. Это нужно чтобы потом в личном календаре студента отображалась дата, когда он проходил тестирование
  $sql2="update calendar_events set PUPIL_NUM_DOGOVOR=? where UUID_IND_ZAYAV=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($num_dog[0], $row_zayav [16]);

  #Перенос заявки в архив
  $sql2="insert into zayavki_archive (DATE_GET_ZAYAV, WHO_GET_ZAYAV, SOURCE_ZAYAV, FIO_STUDENT, FIO_PARENT, AGE_STUDENT, LANGUAGE, LEVEL_KNOWLEDGE, BRANCH, PHONE, SOURCE_ABOUT_US, DATE_OF_TEST, TIME_OF_TEST, NOTES, USER_ID, UUID_IND, DATE_OF_BORN, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,now())";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($row_zayav[1], $row_zayav[2], $row_zayav[3], $row_zayav[4], $row_zayav[5], $row_zayav[6], $row_zayav[7], $row_zayav[8], $row_zayav[9], $row_zayav[10], $row_zayav[11], $row_zayav[12], $row_zayav[13], $row_zayav[14], $us_id, $row_zayav[16], $row_zayav[17]);
 
  
  #Удаление перенесенной заявки из таблицы zayavki
  $sql2="delete from zayavki where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($idd);
  
  $dbh2->commit; #Завершение транзакции
  $dbh2->{AutoCommit}=1; 
  $dbh2->{RaiseError}=0;
  };
  if ($@) # если произошла ошибка, то откатываем транзакцию
  {
  # откат внутри eval, чтобы ошибка отката не привела к завершению работы сценария
  eval { $dbh2->rollback; };
  }
  $dbh2->disconnect; 
  ################################################

  my $ans="true";
  #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({success => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################

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

__END__
