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

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $us_id=$sess->param('USER_ID');
my $able_add_period_of_pays=$sess->param('able_add_period_of_pays');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

   if ($able_add_period_of_pays==1) #������� ����� �� ���������� ������������ ��������� ������ ������. ��������� ��� �� ���������� ����������� �� ������.
   {
        my $summ=param('SUMM_PAY');   
        my $num_dog=param('num_dogovor_student');
        $summ=~s/\0//g; $summ=~s/\.\.//g; $summ=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $num_dog=~s/\0//g; $num_dog=~s/\.\.//g; $num_dog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        ########�������� �� ���� ����� ������
        if (length($summ)==0)
        {
          my $ans="���������� ��������� ����� ��� ������!";
          #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
          my $res=$ans;

          #convert  data to JSON
          my $op = JSON -> new -> pretty(1);
          my $json = $op -> encode({result => $res});

          print $cgi->header('application/json;charset=windows-1251');
          print $json;
          exit;
        }
        ##############################################################
        
        ########�������� �� ������������ ����� �������
        if ($summ!~m/^\s*\d+\.\d+\s*$/is)
        {
          my $ans="��������� ����� ��� ������ �� ���������! ������ ������ ����, ��������, 2000.00";
          #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
          my $res=$ans;

          #convert  data to JSON
          my $op = JSON -> new -> pretty(1);
          my $json = $op -> encode({result => $res});

          print $cgi->header('application/json;charset=windows-1251');
          print $json;
          exit;
        }
        ##############################################################
        
        #######################�������� GROUP_ID �� ������� groups_students ��� ��� ������� � ������� pays ��� �������� ������ ������� ������###########################
        my $dbh0=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth0=$dbh0->do("SET NAMES 'cp1251'");
        my $sql0="select GROUP_ID from groups_students where PUPILS_NUM_DOGOVOR=?";
        $sth0=$dbh0->prepare($sql0);
        $sth0->execute($num_dog);
        #� ������ ���������� ����������� ������
        my @gr_id = $sth0->fetchrow_array;
		
		#######################�������� UUID �� ������� LESSONS ��� ��� ������� � ������� calendar_pupils ��� �������� ������ ������� ������###########################
        my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth5=$dbh5->do("SET NAMES 'cp1251'");
        my $sql5="select lessons.UUID, lessons.DAYS_OF_LESSONS from lessons, groups_students where groups_students.GROUP_ID=lessons.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
        $sth5=$dbh5->prepare($sql5);
        $sth5->execute($num_dog);
        #� ������ ���������� ����������� ������
        my @lesson_data = $sth5->fetchrow_array;
        
        #######################�������� ��� ������� ###########################
        my $dbh6=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth6=$dbh6->do("SET NAMES 'cp1251'");
        my $sql6="select teachers.FIO from teachers, lessons, groups_students where groups_students.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=teachers.ID and groups_students.PUPILS_NUM_DOGOVOR=?";
        $sth6=$dbh6->prepare($sql6);
        $sth6->execute($num_dog);
        #� ������ ���������� ����������� ������
        my @fio_teacher = $sth6->fetchrow_array;                
        
        #######################�������� ��������� ������������ ������ ������ � ��������. ��� ����� ��� ����� �������� ��������� ������  � ��������� ���������� �������  ###########################
        my $data_per;
        my @per;
		my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        #my $sql1="select PERIOD from pays where pupils_num_dogovor=? and GROUP_ID=? and id=(select max(id) from pays where pupils_num_dogovor=?)";
		my $sql1="select PERIOD from pays where pupils_num_dogovor=? and GROUP_ID=? order by (SUBSTRING_INDEX(PERIOD, '.', -1)+0), (SUBSTRING_INDEX(PERIOD, '.', 1)+0)";        
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($num_dog, $gr_id[0]);
        #� ������ ���������� ����������� ������
		while ($data_per=$sth1->fetchrow_array) {
        push @per, $data_per;
        }
        #my @per = $sth1->fetchrow_array;
        
        #��������� ���������� ������ �� ����� � ���
        my @period=split(/\./, $per[$#per]);
        
        my ($month, $year, $new_period, $count_days);
        if ($period[0]<12)
        {
           $month=$period[0]+1;
           $year=$period[1];
           $new_period=$month.".".$year;
		   
		   #��������� ���� ��������� month ����� ����� 12, �.�. �������, �� �������� ����� ���������� month_dop � ����������� �� 0, �.�. � ������� ������������ ���-�� ���� � ������ ������� ������������ ��� 0
           if ($month==12)
           {
              my $month_dop=0;
              $count_days=((localtime(timelocal(0,0,0,1,$month_dop,$year-1900)-1))[3]); #���������� ���-�� ���� � ����������� �������/������
           }
           else
           {
              my $month_dop=$month;
              $count_days=((localtime(timelocal(0,0,0,1,$month_dop,$year-1900)-1))[3]); #���������� ���-�� ���� � ����������� �������/������
           }
        }
        if ($period[0]==12)
        {
           $month=1;
           $year=$period[1]+1;
           $new_period=$month.".".$year;
		   $count_days=((localtime(timelocal(0,0,0,1,$month,$year-1900)-1))[3]); #���������� ���-�� ���� � ����������� �������/������
        }        
        
        
        #######################���������� ���������� �������###########################
        my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="insert into pays (PUPILS_NUM_DOGOVOR, PERIOD, SUMM_4_OPL, OPL_SUMM, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?, now())";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($num_dog, $new_period, $summ, 0, $gr_id[0], $us_id);
		
		#######################���������� ���������� ������� ���������###########################
        my $dbh22=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth22=$dbh22->do("SET NAMES 'cp1251'");
        my $sql22="insert into visits (PUPILS_NUM_DOGOVOR, PERIOD, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,?, NOW())";
        $sth22=$dbh22->prepare($sql22);
        $sth22->execute($num_dog, $new_period, $gr_id[0], $us_id);              
        
        #######################�������� �����, ���������� ����� ����������, ��������� ����� �������� �� ������ �������� � ID ������ �� ������� pays###########################
        my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth3=$dbh3->do("SET NAMES 'cp1251'");
        my $sql3="select sum(SUMM_4_OPL) from pays where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth3=$dbh3->prepare($sql3);
        $sth3->execute($num_dog, $gr_id[0]);
        #� ������ ���������� ����������� ������
        my @row_new_price_course = $sth3->fetchrow_array;
        
        
        #######################���������� �������������� ��������� ����� ����������� � �������� � ������� groups_students. ��� ���� ������ �.�. ��� ������ ����� ������ ������ � �������������� ����� � ������, ������� ����� ����� ����� ����������###########################
        my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth4=$dbh4->do("SET NAMES 'cp1251'");
        my $sql4="update groups_students set PRICE_COURSE=? where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth4=$dbh4->prepare($sql4);
        $sth4->execute($row_new_price_course[0], $num_dog, $gr_id[0]);
				
		#����������� ���������� ������ (��� ���������� ��� � ����� �������) �� ������� lessons � ������, ����� �� ���� ������ ������ � ������� ��� �������, ����� �� ��� ���������� �� ����� ���� �������� � ������������ ������� ��� ���.
        my @DAYS=split(/\,/, $lesson_data[1]);
                
        #������������� �������� ��� ������ � ���� ��������� �������. � ����� ������ ��� �����, �.�. ����������� ���� ������.
        my $first = $year."-".$month."-"."01";
        my $second = $year."-".$month."-".$count_days;
        
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
            
              #��������� ������ � ������ ��������� ��������� ����������� � ������ ������
              my $dbh8=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
              my $sth8=$dbh8->do("SET NAMES 'cp1251'");
              my $sql8="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
              $sth8=$dbh8->prepare($sql8);
              $sth8->execute($dt_beg, $dt_end, "�������. �������������:  ".$fio_teacher[0], $num_dog, $gr_id[0], $lesson_data[0], $us_id);             
           }
  
          }  
        }
        
        $dbh0->disconnect;       
        $dbh1->disconnect;
        $dbh2->disconnect;
        $dbh3->disconnect;
        $dbh4->disconnect;
		$dbh5->disconnect;
        $dbh6->disconnect;
        
        #������������� Null �������� � ���� IS_MOVED. ��� �������� ��� ����, ����� ������ ������� � �������� � ������ ��� �������� �� ������ � ������.
        my $dbh7=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth7=$dbh7->do("SET NAMES 'cp1251'");
        my $sql7="update pupils set IS_MOVED=Null where num_dogovor=?";
        $sth7=$dbh7->prepare($sql7);
        $sth7->execute($num_dog);     
    
        my $ans="������ �������� �������!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
        my $ans="�� �� ������ ����� ��������� ������ ��� ������!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
   }
   
#�������� ������
      sub f_delete_session {
       #������� ����
       my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
       print "Set-Cookie: $cookies\n";
       #������� ������
       $sess->delete();
       $sess->flush();
      }
}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
