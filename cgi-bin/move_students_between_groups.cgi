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

#use Log::Any qw($log);
#use Log::Any::Adapter ('Stdout');
#use Log::Any::Adapter ('File', 'file.log');
#use Log::Any::For::Std;

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
my $able_move_students_between_groups=$sess->param('able_move_students_between_groups');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

  if ($able_move_students_between_groups==1) #Смотрим имеет ли возможноть пользователь производить перемещение между группами студентов. Определям это по парамметру переданному из сессии.
  {  
     my @data=param('dat');

     if (scalar(@data)!=2)
     {
        my $ans="Не корректно переданы данные!";
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
     }  

     foreach my $ch (@data)
     {
        $ch=~s/\0//g;
        $ch=~s/\.\.//g;
        $ch=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
     }

     foreach my $check (@data)
     {
        if ($check!~m/^\d+$/g)
        {
          my $ans="Не корректно переданы идентификаторы!";
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


     ##############################Определяем, созданы ли у группы, в которую переносим студента, занятия. Если нет, то переносить нельзя!
     my $dbh0=ConnectDB->connect;
     my $sth0=$dbh0->do("SET NAMES 'cp1251'");
     my $sql0="select GROUP_ID from lessons where GROUP_ID=?";
     $sth0=$dbh0->prepare($sql0); #Для операций которые не возвращают значение
     $sth0->execute($data[1]);
     my @lessons = $sth0->fetchrow_array; 
  
     if (!@lessons)
     {
        my $ans="Перемещение студента в выбранную группу невозможно, т.к. у группы не созданы занятия"; 
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});
 
        print $cgi->header('application/json;charset=windows-1251');
        print $json; 
        exit;
     }
     ##################################################################################
  
     ##############################Определяем наименование и другие парамметры текущей группы
     my $dbh1=ConnectDB->connect;
     my $sth1=$dbh1->do("SET NAMES 'cp1251'");
     my $sql1="select kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, groups.GROUP_NAME, groups.START_DATE, groups.END_DATE, groups.COURSE_PRICE from groups, groups_students, kind_languages, kind_programm where kind_languages.ID=groups.LANGUAGE and kind_programm.ID=groups.KIND_PROGRAMM and groups.ID=groups_students.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
     $sth1=$dbh1->prepare($sql1); #Для операций которые не возвращают значение
     $sth1->execute($data[0]);
     my @param_gr = $sth1->fetchrow_array; 
  
     if (!@param_gr)
     {
        my $ans="Перемещение студента в выбранную группу невозможно, т.к. студент вообще не привязан к какой-либо группе. В данном случае в перемещении нет необходимости, т.к. данного студента можно сразу привязать к нужной группе"; 
        #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json; 
        exit;
     }
     ##################################################################################
 
 
     ################################### По номеру договора в таблицах изменяем ID группы на выбранный, таким образом производится перенос студента из группы в группу.
  
     #Используем метод транзакций и блок Eval с переменной $@, если произошла ошибка во время выполнения SQL команд в блоке Eval, то выполняем откат операций
     my $dbh=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
     my $sth=$dbh->do("SET NAMES 'cp1251'");
     eval {  

     #############Производим изменения группы в таблице calendar_pupils
     my $sql="update calendar_pupils set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[1], $data[0]);
  
  
     #############Производим изменение группы в таблице pays
     $sql="update pays set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[1], $data[0]);
  
  
     #############Производим изменение группы в таблице groups_students
     $sql="update groups_students set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[1], $data[0]);

    #############?????????? ????????? ????????? ??????? ? ??????? visits
    $sql="update visits set GROUP_ID=? where PUPILS_NUM_DOGOVOR=?";
    $sth=$dbh->prepare($sql); #??? ???????? ??????? ?? ?????????? ????????
    $sth->execute($data[1], $data[0]);
 
     #############Вставляем запись о переводе в историю студента
     $sql="insert into history_students (PUPILS_NUM_DOGOVOR, TEXT, DATETIME_CREATE, USER_ID) values (?,?,NOW(),?)";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[0], 'Перевод из группы: '.$param_gr[2].' (Язык: '.$param_gr[0].', Программа: '.$param_gr[1].', Цена курса: '.$param_gr[5].', Период действия группы: с '.$param_gr[3].' по '.$param_gr[4].')', $us_id);
 
     #############В поле IS_MOVED вставляем 1, как указатель на то, что студент был перемещен между группами
     $sql="update pupils set IS_MOVED=1 where Num_dogovor=?";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[0]);
 
     #############Удаляем существующие записи из каленларя студента (расписание занятий), для вставки расписания из группы в которую перенесен студент
     $sql="delete from calendar_pupils where PUPILS_NUM_DOGOVOR=?";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[0]);
  
     #Получем данные о занятиях привязанных к группе, куда переносим студента, чтобы сделать ему расписание
     $sql="select UUID, TEACHER_ID, ALL_LESSONS from lessons where GROUP_ID=?";
     $sth=$dbh->prepare($sql); #Для операций которые не возвращают значение
     $sth->execute($data[1]);  
     my @row_data = $sth->fetchrow_array;
  
     #Получаем ФИО препода для вставки его в описание занятий в расписании студента
     $sql="select FIO from teachers where ID=?";
     $sth=$dbh->prepare($sql);
     $sth->execute($row_data[1]);
     #В массив записываем извлеченную строку
     my @row_teacher = $sth->fetchrow_array;
     ################################################ 
 
     #Преобразовываем строку полученную из DAYS_OF_LESSONS в массив
     my @full_day_time_data=split(",", $row_data[2]);
    
     #Вставляем данные в личный календарь студентов привязанных к данной группе
     for (my $t9=0; $t9<=$#full_day_time_data; $t9=$t9+3)
     {  
        $sql="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
        $sth=$dbh->prepare($sql);
        $sth->execute($full_day_time_data[$t9]." ".$full_day_time_data[$t9+1], $full_day_time_data[$t9]." ".$full_day_time_data[$t9+2], "Занятия. Преподаватель:  ".$row_teacher[0], $data[0], $data[1], $row_data[0], $us_id);
     }
 
  
     $dbh->commit; #Завершение транзакции
     $dbh->{AutoCommit}=1; 
     $dbh->{RaiseError}=0;
     };
     if ($@) # если произошла ошибка, то откатываем транзакцию
     {
       # откат внутри eval, чтобы ошибка отката не привела к завершению работы сценария
     eval { $dbh->rollback; };
     }
     $dbh->disconnect; 
     ################################################


     my $ans="Перемещение выполнено удачно!";
     #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
     my $res=$ans;

     #convert  data to JSON
     my $op = JSON -> new -> pretty(1);
     my $json = $op -> encode({result => $res});

     print $cgi->header('application/json;charset=windows-1251');
     print $json;
     ############################################################
  }
  else
  {
     my $ans="Вы не имеете права перемещать студентов!";
     #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
     my $res=$ans;

     #convert  data to JSON
     my $op = JSON -> new -> pretty(1);
     my $json = $op -> encode({result => $res});

     print $cgi->header('application/json;charset=windows-1251');
     print $json;
  }

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
