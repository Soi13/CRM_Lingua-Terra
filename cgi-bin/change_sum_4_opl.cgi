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
my $able_change_summ=$sess->param('able_change_summ_4_opl');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

   if ($able_change_summ==1) #Смотрим имеет ли возможноть пользователь изменять сумму к оплате. Определям это по парамметру переданному из сессии.
   {
        my $id=param('id_pay');
        my $new_summ=param('CHANGE_SUM_PAY');   
        my $num_dog=param('num_dogovor_stud');                        
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $new_summ=~s/\0//g; $new_summ=~s/\.\.//g; $new_summ=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $num_dog=~s/\0//g; $num_dog=~s/\.\.//g; $num_dog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        ########Проверка на ввод суммы оплаты
        if (length($new_summ)==0)
        {
          my $ans="Необходимо заполнить сумму для оплаты!";
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
        if ($new_summ!~m/^\s*\d+\.\d+\s*$/is)
        {
          my $ans="Введенная сумма для оплаты не корректна! Формат должен быть, например, 2000.00";
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
        
        #######################Получаем номер договора студента и ID группы по ID из таблицы pays###########################
        my $dbh0=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth0=$dbh0->do("SET NAMES 'cp1251'");
        my $sql0="select PUPILS_NUM_DOGOVOR, GROUP_ID from pays where ID=?";
        $sth0=$dbh0->prepare($sql0);
        $sth0->execute($id);
        #В массив записываем извлеченную строку
        my @row_num_dog = $sth0->fetchrow_array;
                
        
        #######################Производим редактирование суммы платежа###########################
        my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="update pays set SUMM_4_OPL=? where ID=?";
        $sth=$dbh->prepare($sql);
        $sth->execute($new_summ, $id);
              
        
        #######################Получаем общую, измененную после редактирования, стоимость курса студента по номеру договора и ID группы из таблицы pays###########################
        my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        my $sql1="select sum(SUMM_4_OPL) from pays where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($row_num_dog[0], $row_num_dog[1]);
        #В массив записываем извлеченную строку
        my @row_new_price_course = $sth1->fetchrow_array;
        
        
        #######################Производим редактирование стоимости курса сохраненной у студента в таблице groups_students. Это надо делать т.к. было редактирование суммы периода и общая сумма курса изменилась###########################
        my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update groups_students set PRICE_COURSE=? where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($row_new_price_course[0], $row_num_dog[0], $row_num_dog[1]);
        
        
        ##############Блок распределения оплаченных сумм после внесения пользователем изменений в суммах для оплат######################
        my @row;
        my @data;

        my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth3=$dbh3->do("SET NAMES 'cp1251'");
        my $sql3="select ID, SUMM_4_OPL, OPL_SUMM from pays where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth3=$dbh3->prepare($sql3);
        $sth3->execute($row_num_dog[0], $row_num_dog[1]);

        while (@data=$sth3->fetchrow_array) {
        push @row, @data;
        }
        $dbh3->disconnect;

        my $res;
        my $res_nedoplata;
        my $pereplata;
        my $nedoplata;

       for (my $i=0; $i<=$#row; $i=$i+3)
       {
         #Если сумма к оплате и оплаченная сумма равны
         if ($row[$i+2]==$row[$i+1])
         {
            next;    
         } 
   
         #Если оплаченная сумма больше суммы к оплате  
         if ($row[$i+2]>$row[$i+1])
         {     
            $pereplata=$row[$i+2]-$row[$i+1];
            $res=$row[$i+2]-$pereplata; 
     
            my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
            my $sth4=$dbh4->do("SET NAMES 'cp1251'");
          
            #Правим оплаченную сумму в текущей записи
            my $sql4="update pays set OPL_SUMM=? where ID=?";
            $sth4=$dbh4->prepare($sql4);
            $sth4->execute($res, $row[$i]);     
     
            $row[$i+2]=$res;
     
            #Правим путем прибавления, следующую за текущей записью
            my $sql4="update pays set OPL_SUMM=OPL_SUMM+? where ID=?";
            $sth4=$dbh4->prepare($sql4);
            $sth4->execute($pereplata, $row[$i+3]);
     
            $row[$i+5]=$row[$i+5]+$pereplata;
         }
   
   
         #Если оплаченная сумма меньше суммы к оплате
         if ($row[$i+2]<$row[$i+1])
         {     
            $nedoplata=$row[$i+1]-$row[$i+2];
     
            if ($row[$i+5]>=$nedoplata)
            { 
               $res_nedoplata=$row[$i+5]-$nedoplata;
       
               #Правим недоплату в текущей записи
               my $dbh5=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
               my $sth5=$dbh5->do("SET NAMES 'cp1251'");
               my $sql5="update pays set OPL_SUMM=OPL_SUMM+? where ID=?";
               $sth5=$dbh5->prepare($sql5);
               $sth5->execute($nedoplata, $row[$i]);
        
               $row[$i+2]=$row[$i+2]+$nedoplata;
                
               #Правим сумму в следующей записи, т.к. мы из этой суммы вычли суммы недоплаты
               my $dbh6=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
               my $sth6=$dbh6->do("SET NAMES 'cp1251'");
               my $sql6="update pays set OPL_SUMM=? where ID=?";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute($res_nedoplata, $row[$i+3]);
        
               $row[$i+5]=$res_nedoplata;
			   next;
            
            }
			
			if (($row[$i+5]<$nedoplata) && ($row[$i+5]!=0))            
            { 
               #$res_nedoplata=$row[$i+5]-$nedoplata;
       
               #Правим недоплату в текущей записи
               my $dbh5=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
               my $sth5=$dbh5->do("SET NAMES 'cp1251'");
               my $sql5="update pays set OPL_SUMM=OPL_SUMM+? where ID=?";
               $sth5=$dbh5->prepare($sql5);
               $sth5->execute($row[$i+5], $row[$i]);
        
               $row[$i+2]=$row[$i+2]+$row[$i+5];
                
               #Правим сумму в следующей записи, т.к. мы из этой суммы вычли суммы недоплаты
               my $dbh6=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
               my $sth6=$dbh6->do("SET NAMES 'cp1251'");
               my $sql6="update pays set OPL_SUMM=? where ID=?";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute("0", $row[$i+3]);
        
               $row[$i+5]=0;
               next;
            }
     
         }
      }
      #################################################################################################################################
        
        
        $dbh0->disconnect;       
        $dbh->disconnect;
        $dbh1->disconnect;
        $dbh2->disconnect;
		
		#Устанавливаем Null студенту в поле IS_MOVED. Это делается для того, чтобы убрать пометку у студента в случае его переноса из группы в группу.
        my $dbh7=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth7=$dbh7->do("SET NAMES 'cp1251'");
        my $sql7="update pupils set IS_MOVED=Null where num_dogovor=?";
        $sth7=$dbh7->prepare($sql7);
        $sth7->execute($num_dog);
    
        my $ans="Сумма изменена успешно!";
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
        my $ans="Вы не имеете права изменять сумму для оплаты!";
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
