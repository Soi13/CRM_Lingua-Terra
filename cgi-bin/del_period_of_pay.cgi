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
my $able_del_period_of_pays=$sess->param('able_del_period_of_pays');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

   if ($able_del_period_of_pays==1) #Смотрим имеет ли возможноть пользователь удалять периоды. Определям это по парамметру переданному из сессии.
   {
        my $id=param('id_pay');
		my $per_pay=param('per_pay');
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
		$per_pay=~s/\0//g; $per_pay=~s/\.\.//g; $per_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        #######################Смотрим, был ли платеж в выбранном периоде, если был, то удалять нельзя!###########################
        my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select OPL_SUMM from pays where ID=?";
        $sth=$dbh->prepare($sql);
        $sth->execute($id);
        #В массив записываем извлеченную строку
        my @row_pay = $sth->fetchrow_array;
        $dbh->disconnect;        
        if ($row_pay[0]!=0)
        {
            my $ans="В выбранном периоде осуществлен платеж. Данный период удалить невозможно!";
            #Encode::from_to($ans,'utf8','windows-1251');  #Этот перекодировщик используется если данные передаются с frontend через ajax в backend и потом обратно
            my $res=$ans;

            #convert  data to JSON
            my $op = JSON -> new -> pretty(1);
            my $json = $op -> encode({result => $res});

            print $cgi->header('application/json;charset=windows-1251');
            print $json;
            exit;
        }
        ###############################################################################################################################
       
       
        #######################Определяем номер договора студента и ID группы по строке платежа, который хотим удалить. Это для того чтобы у этого студент изменить общую сумму к оплате после удаления одного из  периодов###########################
        my $dbh1=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        my $sql1="select PUPILS_NUM_DOGOVOR, GROUP_ID from pays where ID=?";
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($id);
        #В массив записываем извлеченную строку
        my @row_data = $sth1->fetchrow_array;
		
		#Разбиваем полученный период на месяц и год
        my @period=split(/\./, $per_pay);
		
		#Определяем месяц, для этого смотрим первый элемент массива @period (это месяц), если месяц равен 12 (декабрь), то его надо преобразовать в 0, т.к. функции определения кол-ва дней в месяце, декабрь обозначается как 0
        my $month;
        if ($period[0]==12) { $month==0; } else { $month=$period[0]; }
        
        #Определяем кол-во дней в удаляемом периоде/месяце
        my $count_days=((localtime(timelocal(0,0,0,1,$month,$period[1]-1900)-1))[3]);
        
        #Строим диапазон дат удаляемого периода (дата начала месяца и дата окончания месяца), для вставки их в запрос
        my $date_begin=$period[1]."-".$period[0]."-"."01";
        my $date_end=$period[1]."-".$period[0]."-".$count_days;
        
                      
        #Если платежей в ввыбранном периоде не было, то можно удалять
        my $dbh2=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="delete from pays where ID=?";
        $sth2=$dbh2->prepare($sql2); #Для операций которые не возвращают значение
        $sth2->execute($id);  
        $dbh2->disconnect;
		
		#Также удаляем занятия из календаря студента
        my $dbh5=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth5=$dbh5->do("SET NAMES 'cp1251'");
        my $sql5="delete from calendar_pupils where pupils_num_dogovor=? and GROUP_ID=? and START_DATE between ? and ? and END_DATE between ? and ?";
        $sth5=$dbh5->prepare($sql5); #Для операций которые не возвращают значение
        $sth5->execute($row_data[0], $row_data[1], $date_begin." 00:00:00", $date_end." 23:59:59", $date_begin." 00:00:00", $date_end." 23:59:59");  
        $dbh5->disconnect;

        
        #######################Подсчитываем общую сумму курса для студента после удаления одного из периодов для внесения ее в стоимость курса студента в таблицу groups_students###########################
        my $dbh3=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth3=$dbh3->do("SET NAMES 'cp1251'");
        my $sql3="select sum(SUMM_4_OPL) from pays where GROUP_ID=? and PUPILS_NUM_DOGOVOR=?";
        $sth3=$dbh3->prepare($sql3);
        $sth3->execute($row_data[1], $row_data[0]);
        #В массив записываем извлеченную строку
        my @row_res_summ = $sth3->fetchrow_array;
        
        
        #######################Обновляем стоимость курса у студента в таблице groups_students###########################
        my $dbh4=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth4=$dbh4->do("SET NAMES 'cp1251'");
        my $sql4="update groups_students set PRICE_COURSE=? where GROUP_ID=? and PUPILS_NUM_DOGOVOR=?";
        $sth4=$dbh4->prepare($sql4);
        $sth4->execute($row_res_summ[0], $row_data[1], $row_data[0]);
        
        #Устанавливаем Null студенту в поле IS_MOVED. Это делается для того, чтобы убрать пометку у студента в случае его переноса из группы в группу.
        my $dbh7=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth7=$dbh7->do("SET NAMES 'cp1251'");
        my $sql7="update pupils set IS_MOVED=Null where num_dogovor=?";
        $sth7=$dbh7->prepare($sql7);
        $sth7->execute($row_data[0]);        
        
        my $ans="Период удален успешно!";
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
        my $ans="Вы не имеете права удалять периоды!";
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
