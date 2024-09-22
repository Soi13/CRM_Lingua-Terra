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
use Date::Calc qw(:all);
use Time::Local;

my $SID;
my $method;
my $cgi=CGI->new;

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
        
my $start_date=param('start_date');
my $end_date=param('end_date');
my $idd_gr=param('idd_gr');
my $teach_id=param('TEACHER_ID_ED');
my $room_id=param('ROOM_ID_ED');
$start_date=~s/\0//g; $start_date=~s/\.\.//g; $start_date=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$end_date=~s/\0//g; $end_date=~s/\.\.//g; $end_date=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$idd_gr=~s/\0//g; $idd_gr=~s/\.\.//g; $idd_gr=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$teach_id=~s/\0//g; $teach_id=~s/\.\.//g; $teach_id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$room_id=~s/\0//g; $room_id=~s/\.\.//g; $room_id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#Получаем данные по занятиям для редактирования
my @LESSONS_4_EDIT=param('LESSONS_4_EDIT');

if (@LESSONS_4_EDIT)
{
  #Проверяем и Очищаем массив от всякой херни
  for (my $g=0; $g<=$#LESSONS_4_EDIT; $g++)
  {
        $LESSONS_4_EDIT[$g]=~s/\0//g;
        $LESSONS_4_EDIT[$g]=~s/\.\.//g;
        $LESSONS_4_EDIT[$g]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;        
  }
  ############# 
  
  ###Проверяем, все ли поля по занятиям заполнены.
  for (my $u=0; $u<=$#LESSONS_4_EDIT; $u++)
  {        
        if (($LESSONS_4_EDIT[$u] eq '') || ($LESSONS_4_EDIT[$u] eq ' '))
        {
                my $ans="Не полностью заполнена информация о занятиях!";
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

  ##Проверяем, корректно ли введена дата занятия Не написал ли туда юзер всякой херни)))
  for (my $u1=0; $u1<=$#LESSONS_4_EDIT; $u1=$u1+4)
  {
        ## Вообще, здесь можно применить вот это выражение: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. Оно сразу не дает вводить некорректные даты и месяцы (например больше 12). Я оставил свое, чтобы можно было пользователя информировать, что он некорректно ввел например месяц или дату.
        if ($LESSONS_4_EDIT[$u1]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
        {
                my $ans="Введенная дата занятия не корректна. Формат должен быть, например, 2016-05-30";
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
        $LESSONS_4_EDIT[$u1]=~/(?<=-)(\d{2})(?=-)/;
        if ($&>12)
        {
                my $ans="В введенной дате занятия не корректен месяц. Месяц не может быть больше 12!";
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
        $LESSONS_4_EDIT[$u1]=~/\d{4}/;
        if ($&>3000)
        {
                my $ans="В введенной дате занятия не разумно большой год.";
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
        $LESSONS_4_EDIT[$u1]=~/(?<=-)(\d{2})$/;
        if ($&>31)
        {
                my $ans="В введенной дате занятия не корректно задано число! Число не может быть более 31!";
                #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        
        ########Сравнение дат, чтобы пользователь случайно не ввел дату занятия меньше даты начала курса и больше даты окончания курса
        my @f = ($start_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
        my @e = ($LESSONS_4_EDIT[$u1] =~ /^(\d+)\-(\d+)\-(\d+)$/);
        my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
        my $sepoch = timelocal(0,0,0,$e[2],$e[1]-1,$e[0]);
        if ($fepoch>$sepoch)
        {
          my $ans="Введенная дата занятия меньше даты начала курса!";
          #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
          my $res=$ans;

          #convert  data to JSON
          my $op = JSON -> new -> pretty(1);
          my $json = $op -> encode({result => $res});

          print $cgi->header('application/json;charset=windows-1251');
          print $json;
          exit;
        }
        
        
        my @f1 = ($end_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
        my @e1 = ($LESSONS_4_EDIT[$u1] =~ /^(\d+)\-(\d+)\-(\d+)$/);
        my $fepoch1 = timelocal(0,0,0,$f1[2],$f1[1]-1,$f1[0]);
        my $sepoch1 = timelocal(0,0,0,$e1[2],$e1[1]-1,$e1[0]);
        if ($fepoch1<$sepoch1)
        {
          my $ans="Введенная дата занятия больше даты окончания курса!";
          #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
          my $res=$ans;

          #convert  data to JSON
          my $op = JSON -> new -> pretty(1);
          my $json = $op -> encode({result => $res});

          print $cgi->header('application/json;charset=windows-1251');
          print $json;
          exit;
        }
        ############################################################################################
  }
  

  ##Проверяем, корректно ли введено время занятий? Не написал ли туда юзер всякой херни)))
  for (my $u2=1; $u2<=$#LESSONS_4_EDIT; $u2=$u2+4)
  {
        #Проверяем первый элемент массива, т.к. он содержит начальное врем занятий, а потом второй, путем прибавления единички к индексу массива
        if ($LESSONS_4_EDIT[$u2]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
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
        
        if ($LESSONS_4_EDIT[$u2+1]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
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

  }
=head  
  ##Проверяем, чтобы время начала занятий не было меньше окончания занятий
  for (my $u3=1; $u3<=$#LESSONS_4_EDIT; $u3=$u3+4)
  {
        
        #Проверяем, чтобы время начала занятий не было меньше окончания занятий
        my $t1 = $LESSONS_4_EDIT[$u3];
        my $t2 = $LESSONS_4_EDIT[$u3+1];

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
        
        my $time1= undef;
        my $time2= undef;
  }
=cut
}

#Получаем номера договоров всех студентов привязанных к группе, чтобы сформировать им личный календарь занятий
my $data4;
my @row_dogovors;
my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($idd_gr);
#В массив записываем извлеченные строки
while ($data4=$sth4->fetchrow_array) {
push  @row_dogovors, $data4;
}
$dbh4->disconnect;
################################################


#Получаем ФИО препода по ID переданному с формы
my $dbh5=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth5=$dbh5->do("SET NAMES 'cp1251'");
my $sql5="select FIO from teachers where ID=?";
$sth5=$dbh5->prepare($sql5);
$sth5->execute($teach_id);
#В массив записываем извлеченную строку
my @row_teacher = $sth5->fetchrow_array;
$dbh5->disconnect;
################################################


#Определяем UUID занятия привязанного к группе
my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select UUID from lessons where GROUP_ID=?";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($idd_gr);
#В массив записываем извлеченную строку
my @row_uuid = $sth1->fetchrow_array;
$dbh1->disconnect;
################################################
 

#Обновляем данные по преподу и комнате занятий 
my $dbh0=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth0=$dbh0->do("SET NAMES 'cp1251'");
my $sql0="update lessons set TEACHER_ID=?, ROOM_ID=? where GROUP_ID=?";
$sth0=$dbh0->prepare($sql0);
$sth0->execute($teach_id, $room_id, $idd_gr);
$dbh0->disconnect;
################################################


#Идем по массиву и производим редактирование занятий
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
for (my $g1=0; $g1<=$#LESSONS_4_EDIT; $g1=$g1+4)
{
   my @f = ($LESSONS_4_EDIT[$g1] =~ /^(\d+)\-(\d+)\-(\d+)$/);
   my $days = Day_of_Week($f[0],$f[1],$f[2]);
   $days=0 if ($days==7);
   
   my $sql="update lessons_list set WEEK_DAY=?, DATE_LESSON=?, TIME_BEGIN=?, TIME_END=?, USER_ID_UPDATE=?, DATETIME_UPDATE=NOW() where ID=?";
   $sth=$dbh->prepare($sql);
   $sth->execute($days, $LESSONS_4_EDIT[$g1], $LESSONS_4_EDIT[$g1+1], $LESSONS_4_EDIT[$g1+2], $us_id, $LESSONS_4_EDIT[$g1+3]);
}
$dbh->disconnect;

#Удаляем записи по UUID из таблицы lessons_group (Календарь группы), чтобы потом вставить новые. Таким образом происходит обновление, т.к update сделать здесь не получается
my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="delete from lessons_group where UUID_LESSONS=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($row_uuid[0]);
$dbh2->disconnect;
################################################

#Удаляем записи по UUID из таблицы calendar_pupils (Календарь студента), чтобы потом вставить новые. Таким образом происходит обновление, т.к update сделать здесь не получается
my $dbh6=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth6=$dbh6->do("SET NAMES 'cp1251'");
my $sql6="delete from calendar_pupils where UUID_LESSONS=?";
$sth6=$dbh6->prepare($sql6);
$sth6->execute($row_uuid[0]);
$dbh6->disconnect;
################################################


#Идем по массиву и производим вставку занятий в таблицу lessons_group
my @calend_of_lessons;  
my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
for (my $g2=0; $g2<=$#LESSONS_4_EDIT; $g2=$g2+4)
{
   #my @f = ($LESSONS_4_EDIT[$g2] =~ /^(\d+)\-(\d+)\-(\d+)$/);
   #my $days = Day_of_Week($f[0],$f[1],$f[2]);
   #$days=0 if ($days==7);
   
   my $sql3="insert into lessons_group (START_DATE, END_DATE, TEXT_MESSAGE, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?, NOW())";
   $sth3=$dbh3->prepare($sql3);
   $sth3->execute($LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+1], $LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+2], "Занятия. Преподаватель:  ".$row_teacher[0], $row_uuid[0], $us_id);
   
   push @calend_of_lessons, $LESSONS_4_EDIT[$g2], $LESSONS_4_EDIT[$g2+1], $LESSONS_4_EDIT[$g2+2];
   
   #Вставляем данные в личный календарь студентов привязанных к данной группе
   foreach my $num_dg (@row_dogovors)
   {             
    $sql3="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
    $sth3=$dbh3->prepare($sql3);
    $sth3->execute($LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+1], $LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+2], "Занятия. Преподаватель:  ".$row_teacher[0], $num_dg, $idd_gr, $row_uuid[0], $us_id);
   } 
   
}
$dbh3->disconnect;

#Преобразуем массив @calend_of_lessons в строку, чтобы можно было его вставить в БД  
my $cal_less=join(",", @calend_of_lessons);

##Вставляем строку с полным списком дат и времени занятий. Это для того, чтобы при привязке студента отсюда считывать инфу.
my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="update lessons set ALL_LESSONS=? where UUID=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($cal_less, $row_uuid[0]);
$dbh4->disconnect;


my $res1="Занятия отредактированы успешно!";
my $op1=JSON->new->pretty(1);
my $json1=$op1->encode({result => $res1});
#my $json=$op->encode(\@res);
print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json1;


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