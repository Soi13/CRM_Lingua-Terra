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
use Date::Calc qw(:all);

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

###############Получение массива дней занятий и диапазона времени. Для этого используется поле DAYS. Они передается как массивы значений.
my $query=CGI->new;
my @DAYS = $query->param('DAYS');

foreach my $n (@DAYS)
{
        $n=~s/\0//g;
        $n=~s/\.\.//g;
        $n=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;        
}

#Получение остальных полей. Записываем их в массив.
my @form_fields=(param('TEACHER_ID'), param('ROOM_ID'), param('id_gr'));

foreach my $m (@form_fields)
{
        $m=~s/\0//g;
        $m=~s/\.\.//g;
        $m=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;        
}

########Проверка на ввод Преподавателя
if (length($form_fields[0])==0)
{
  my $ans="Необходимо заполнить \"Преподаватель\"!";
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

########Проверка на ввод Только корректных Преподов
my $dbh_t=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_t=$dbh_t->do("SET NAMES 'cp1251'");

my $sql_t="select ID from teachers where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_t=$dbh_t->prepare($sql_t);
$sth_t->execute($form_fields[0]);
my $cnt_t=$sth_t->rows();
$dbh_t->disconnect();

if ($cnt_t==0)
{
  my $ans="Поле \"Преподаватель\" должно содержать только данные из списка!";
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

########Проверка на ввод Аудитории
if (length($form_fields[1])==0)
{
  my $ans="Необходимо заполнить \"Аудиторию\"!";
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

########Проверка на ввод Только корректных Аудиторий
my $dbh_br=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from rooms where ID=?"; #Используем ID,т.к. combobox при выборе наименования филиала возвращает его ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[1]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="Поле \"Аудитория\" должно содержать только данные из списка!";
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


#### Если данные массивы не пусты, т.е. значение не равно -1, то выполняем запрос на вставку данных
if ($#DAYS ne '-1'){

###Проверяем, все ли поля по дням и времени заполнены.
for (my $u=0; $u<=$#DAYS; $u++)
{
        if (($DAYS[$u] eq '') || ($DAYS[$u] eq ' '))
        {
                my $ans="Не полностью заполнена информация о днях и времени занятий!";
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

##Проверяем, корректно ли введено время занятий? Не написал ли туда юзер всякой херни)))
for (my $u1=1; $u1<=$#DAYS; $u1=$u1+3)
{
        #Проверяем первый элемент массива, т.к. он содержит начальное врем занятий, а потом второй, путем прибавления единички к индексу массива
        if ($DAYS[$u1]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
        {
                my $ans="Введенное время занятий не корректно. Формат должен быть, например, 03:50 или 22:30";
                #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        if ($DAYS[$u1+1]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
        {
                my $ans="Введенное время занятий не корректно. Формат должен быть, например, 03:50 или 22:30";
                #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        #Проверяем, чтобы время начала занятий не было меньше окончания занятий
        my $t1 = $DAYS[$u1];
        my $t2 = $DAYS[$u1+1];

        # Преобразуем время в число секунд с начала эпохи
        my $time1 = timelocal((reverse split(':', $t1)), (localtime(time))[2..3]);
        my $time2 = timelocal((reverse split(':', $t2)), (localtime(time))[2..3]);

        # Теперь с переменными $time1 и $time2 можно производить сравнение
        if ($time1 >= $time2)
        {
                my $ans="Во времени занятий указан не верный порядок времени. Время начала занятий не может быть больше или равно времени окончания!";
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

 ###################################Проверяем, есть ли уже созданные занятия и препод у группы. Если есть, то прерываем работу программы, т.к. больше одного препода и занятий у него создавать нельзя
  my $dbh0=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth0=$dbh0->do("SET NAMES 'cp1251'");
  my $sql0="select GROUP_ID from lessons where GROUP_ID=?";
  $sth0=$dbh0->prepare($sql0);
  $sth0->execute($form_fields[2]);
  #В массив записываем извлеченную строку
  my @row_gr_id = $sth0->fetchrow_array;
  $dbh0->disconnect;
  if (@row_gr_id)
        {
                my $ans="К данной группе уже привязан преподаватель и созданы занятия!";
                #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
  
  ################################################


  my $dbh2=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  eval {  
  
  ###################################Генерируем UUID для вставки его в таблицу teachers и children_of_teachers. По этому полю будет происходить связь препода и его детей
  my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #В массив записываем извлеченную строку
  my @row_uuid = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################
  
  #Получаем ФИО препода по ID переданному с формы
  my $sql2="select FIO from teachers where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[0]);
  #В массив записываем извлеченную строку
  my @row_teacher = $sth2->fetchrow_array;
  ############################################
 
  my $data;
  my @row_dogovors;
  #Получаем номера договоров всех студентов привязанных к группе, чтобы сформировать им личный календарь занятий
  my $sql2="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2]);
  #В массив записываем извлеченные строки
  while ($data=$sth2->fetchrow_array) {
  push  @row_dogovors, $data;
  }
  ################################################
  
  #Получаем даты начала и окончания курса и его сумму из группы по ID группы переданному с формы
  my $sql2="select START_DATE, END_DATE, COURSE_PRICE from groups where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2]);
  #В массив записываем извлеченную строку
  my @row_data = $sth2->fetchrow_array;
  
  #Проверяем, если даты окончания нет, она не заполнена, то останавливаем работу, т.к. без даты окончания сформировать в этом режиме (По дате окончания) календарь занятий невозможно!
  if ($row_data[1] eq "" || $row_data[1] eq " ")
  {
          my $ans="Выбрана группа без даты окончания курса. В данном режиме невозможно сформировать календарь занятий!"; 
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
  
  #Преобразуем массив @DAYS в строку, чтобы можно было его вставить в БД
  my $res_days=join(",", @DAYS);

  #Вставляем данные в таблицу lessons
  $sql2="insert into lessons (GROUP_ID, TEACHER_ID, ROOM_ID, START_COURSE, END_COURSE, UUID, DAYS_OF_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,NOW())";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2], $form_fields[0], $form_fields[1], $row_data[0], $row_data[1], $row_uuid[0], $res_days, $us_id);
  
  #Создаем занятия для группы и студентов привязанных к данной группе, путем разбивки периода действия группы на даты. Даты вычисляются по дням недели занятий, которые указываются при создании занятий.
  my $first = $row_data[0];
  my $second = $row_data[1];
 
  my @calend_of_lessons;  
 
  my @f = ($first =~ /^(\d+)\-(\d+)\-(\d+)$/);
  my @s = ($second =~ /^(\d+)\-(\d+)\-(\d+)$/);
  my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
  my $sepoch = timelocal(0,0,0,$s[2],$s[1]-1,$s[0]);
  ($fepoch,$sepoch) = ($sepoch,$fepoch) if $fepoch > $sepoch;
  for (my $ind=0; $ind<=$#DAYS; $ind=$ind+3)
  {
    for (my $i=$fepoch; $i <= $sepoch; $i += 24 * 60 * 60) {
       #print scalar localtime($i),"\n";
       my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($i);
       $year=$year+1900;
       #print $mday.".".($mon+1)."    ".$wday,  "\n" if ($wday==1 || $wday==3);     
       if ($wday==$DAYS[$ind])
       {
             my $dt_beg=$year."-".($mon+1)."-".$mday." ".$DAYS[$ind+1];
             my $dt_end=$year."-".($mon+1)."-".$mday." ".$DAYS[$ind+2];
             
			 push @calend_of_lessons, $year."-".($mon+1)."-".$mday, $DAYS[$ind+1], $DAYS[$ind+2];
			 
			 $sql2="insert into lessons_group (START_DATE, END_DATE, TEXT_MESSAGE, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?, NOW())";
             $sth2=$dbh2->prepare($sql2);
             $sth2->execute($dt_beg, $dt_end, "Занятия. Преподаватель:  ".$row_teacher[0], $row_uuid[0], $us_id);
             
             #Вставляем данные для списка занятий
             $sql2="insert into lessons_list (WEEK_DAY, DATE_LESSON, TIME_BEGIN, TIME_END, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?, NOW())";
             $sth2=$dbh2->prepare($sql2);
             $sth2->execute($DAYS[$ind], $dt_beg, $DAYS[$ind+1], $DAYS[$ind+2], $row_uuid[0], $us_id);

             #Вставляем данные в личный календарь студентов привязанных к данной группе
             foreach my $num_dg (@row_dogovors)
             {             
                $sql2="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
                $sth2=$dbh2->prepare($sql2);
                $sth2->execute($dt_beg, $dt_end, "Занятия. Преподаватель:  ".$row_teacher[0], $num_dg, $form_fields[2], $row_uuid[0], $us_id);
             }
             
       } 
  
    }  
  }   
  
#Преобразуем массив @calend_of_lessons в строку, чтобы можно было его вставить в БД  
my $cal_less=join(",", @calend_of_lessons);
#Вставляем строку с полным списком дат и времени занятий. Это для того, чтобы при привязке студента отсюда считывать инфу.  
my $sql2="update lessons set ALL_LESSONS=? where UUID=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($cal_less, $row_uuid[0]);


 #Подсчитываем кол-во месяцев жизни группы.
  my $first_dt = $row_data[0];
  my $second_dt = $row_data[1];
  my @f_dt = ($first_dt =~ /^(\d+)\-(\d+)\-(\d+)$/);
  my @s_dt = ($second_dt =~ /^(\d+)\-(\d+)\-(\d+)$/);
  #my $fepoch_d = timelocal(0,0,0,$f_dt[2],$f_dt[1]-1,$f_dt[0]);
  #my $sepoch_d = timelocal(0,0,0,$s_dt[2],$s_dt[1]-1,$s_dt[0]);
  my $fepoch_d = timelocal(0,0,0,1,$f_dt[1]-1,$f_dt[0]);
  my $sepoch_d = timelocal(0,0,0,Days_in_Month($s_dt[0],$s_dt[1]),$s_dt[1]-1,$s_dt[0]); 
  ($fepoch_d,$sepoch_d) = ($sepoch_d,$fepoch_d) if $fepoch_d > $sepoch_d;
  my $cnt_month=0;
  for (my $i=$fepoch_d; $i <= $sepoch_d; $i += 24 * 60 * 60 * 31) 
  {
     my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($i);
     $cnt_month++;
  }
  
  #Вычисляем стоимость оплаты в месяц путем деления общей стоимости курса на кол-во месяцев.
  my $pay_per_month=$row_data[2]/$cnt_month;
  
  
  #Создаем помесячную разбивку оплат для студентов привязанных к данной группе.
  my $first_date = $row_data[0];
  my $second_date = $row_data[1];
  my @f_date = ($first_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
  my @s_date = ($second_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
  #my $fepoch_dt = timelocal(0,0,0,$f_date[2],$f_date[1]-1,$f_date[0]);
  #my $sepoch_dt = timelocal(0,0,0,$s_date[2],$s_date[1]-1,$s_date[0]);
  my $fepoch_dt = timelocal(0,0,0,1,$f_date[1]-1,$f_date[0]);
  my $sepoch_dt = timelocal(0,0,0,Days_in_Month($s_date[0],$s_date[1]),$s_date[1]-1,$s_date[0]); 
  ($fepoch_dt,$sepoch_dt) = ($sepoch_dt,$fepoch_dt) if $fepoch_dt > $sepoch_dt;
  for (my $i=$fepoch_dt; $i <= $sepoch_dt; $i += 24 * 60 * 60 * 31) 
  {
     my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($i);
     my $period=($mon+1).".".($year+1900);
     
     #Вставляем данные в оплаты студентов привязанных к данной группе
     foreach my $num_dg (@row_dogovors)
     {             
        #Вставляем данные в оплаты студентов привязанных к данной группе
		$sql2="insert into pays (PUPILS_NUM_DOGOVOR, PERIOD, SUMM_4_OPL, OPL_SUMM, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,'0',?,?, NOW())";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($num_dg, $period, $pay_per_month, $form_fields[2], $us_id);
		
		#Вставляем данные в посещения студентов привязанных к данной группе
        $sql2="insert into visits (PUPILS_NUM_DOGOVOR, PERIOD, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,?, NOW())";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($num_dg, $period, $form_fields[2], $us_id);
     }     
     
  }
    
  $dbh2->commit; #Завершение транзакции
  $dbh2->{AutoCommit}=1; 
  $dbh2->{RaiseError}=0;
  };
  if ($@) # если произошла ошибка, то откатываем транзакцию
  {
  # откат внутри eval, чтобы ошибка отката не привела к завершению работы сценария
  eval { $dbh2->rollback; };
  }
  else
  {
    my $ans="Занятия добавлены успешно!"; 
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
  $dbh2->disconnect; 
  ################################################
   
}
else 
{
   my $ans="Невозможно создать занятия для группы без выбора дней и времени занятий!";
   #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
   my $res=$ans;

   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});

   print $cgi->header('application/json;charset=windows-1251');
   print $json;
   exit;
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
