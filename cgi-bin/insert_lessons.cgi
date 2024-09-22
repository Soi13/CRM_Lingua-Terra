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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

###############��������� ������� ���� ������� � ��������� �������. ��� ����� ������������ ���� DAYS. ��� ���������� ��� ������� ��������.
my $query=CGI->new;
my @DAYS = $query->param('DAYS');

foreach my $n (@DAYS)
{
        $n=~s/\0//g;
        $n=~s/\.\.//g;
        $n=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;        
}

#��������� ��������� �����. ���������� �� � ������.
my @form_fields=(param('TEACHER_ID'), param('ROOM_ID'), param('id_gr'));

foreach my $m (@form_fields)
{
        $m=~s/\0//g;
        $m=~s/\.\.//g;
        $m=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;        
}

########�������� �� ���� �������������
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� \"�������������\"!";
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

########�������� �� ���� ������ ���������� ��������
my $dbh_t=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_t=$dbh_t->do("SET NAMES 'cp1251'");

my $sql_t="select ID from teachers where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_t=$dbh_t->prepare($sql_t);
$sth_t->execute($form_fields[0]);
my $cnt_t=$sth_t->rows();
$dbh_t->disconnect();

if ($cnt_t==0)
{
  my $ans="���� \"�������������\" ������ ��������� ������ ������ �� ������!";
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

########�������� �� ���� ���������
if (length($form_fields[1])==0)
{
  my $ans="���������� ��������� \"���������\"!";
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

########�������� �� ���� ������ ���������� ���������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from rooms where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[1]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"���������\" ������ ��������� ������ ������ �� ������!";
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


#### ���� ������ ������� �� �����, �.�. �������� �� ����� -1, �� ��������� ������ �� ������� ������
if ($#DAYS ne '-1'){

###���������, ��� �� ���� �� ���� � ������� ���������.
for (my $u=0; $u<=$#DAYS; $u++)
{
        if (($DAYS[$u] eq '') || ($DAYS[$u] eq ' '))
        {
                my $ans="�� ��������� ��������� ���������� � ���� � ������� �������!";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
}

##���������, ��������� �� ������� ����� �������? �� ������� �� ���� ���� ������ �����)))
for (my $u1=1; $u1<=$#DAYS; $u1=$u1+3)
{
        #��������� ������ ������� �������, �.�. �� �������� ��������� ���� �������, � ����� ������, ����� ����������� �������� � ������� �������
        if ($DAYS[$u1]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
        {
                my $ans="��������� ����� ������� �� ���������. ������ ������ ����, ��������, 03:50 ��� 22:30";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
                my $ans="��������� ����� ������� �� ���������. ������ ������ ����, ��������, 03:50 ��� 22:30";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        #���������, ����� ����� ������ ������� �� ���� ������ ��������� �������
        my $t1 = $DAYS[$u1];
        my $t2 = $DAYS[$u1+1];

        # ����������� ����� � ����� ������ � ������ �����
        my $time1 = timelocal((reverse split(':', $t1)), (localtime(time))[2..3]);
        my $time2 = timelocal((reverse split(':', $t2)), (localtime(time))[2..3]);

        # ������ � ����������� $time1 � $time2 ����� ����������� ���������
        if ($time1 >= $time2)
        {
                my $ans="�� ������� ������� ������ �� ������ ������� �������. ����� ������ ������� �� ����� ���� ������ ��� ����� ������� ���������!";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
       
}

 ###################################���������, ���� �� ��� ��������� ������� � ������ � ������. ���� ����, �� ��������� ������ ���������, �.�. ������ ������ ������� � ������� � ���� ��������� ������
  my $dbh0=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth0=$dbh0->do("SET NAMES 'cp1251'");
  my $sql0="select GROUP_ID from lessons where GROUP_ID=?";
  $sth0=$dbh0->prepare($sql0);
  $sth0->execute($form_fields[2]);
  #� ������ ���������� ����������� ������
  my @row_gr_id = $sth0->fetchrow_array;
  $dbh0->disconnect;
  if (@row_gr_id)
        {
                my $ans="� ������ ������ ��� �������� ������������� � ������� �������!";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
  
  ###################################���������� UUID ��� ������� ��� � ������� teachers � children_of_teachers. �� ����� ���� ����� ����������� ����� ������� � ��� �����
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select UUID()";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute();
  #� ������ ���������� ����������� ������
  my @row_uuid = $sth1->fetchrow_array;
  $dbh1->disconnect;
  ################################################
  
  #�������� ��� ������� �� ID ����������� � �����
  my $sql2="select FIO from teachers where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[0]);
  #� ������ ���������� ����������� ������
  my @row_teacher = $sth2->fetchrow_array;
  ############################################
 
  my $data;
  my @row_dogovors;
  #�������� ������ ��������� ���� ��������� ����������� � ������, ����� ������������ �� ������ ��������� �������
  my $sql2="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2]);
  #� ������ ���������� ����������� ������
  while ($data=$sth2->fetchrow_array) {
  push  @row_dogovors, $data;
  }
  ################################################
  
  #�������� ���� ������ � ��������� ����� � ��� ����� �� ������ �� ID ������ ����������� � �����
  my $sql2="select START_DATE, END_DATE, COURSE_PRICE from groups where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2]);
  #� ������ ���������� ����������� ������
  my @row_data = $sth2->fetchrow_array;
  
  #���������, ���� ���� ��������� ���, ��� �� ���������, �� ������������� ������, �.�. ��� ���� ��������� ������������ � ���� ������ (�� ���� ���������) ��������� ������� ����������!
  if ($row_data[1] eq "" || $row_data[1] eq " ")
  {
          my $ans="������� ������ ��� ���� ��������� �����. � ������ ������ ���������� ������������ ��������� �������!"; 
          #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
          my $res=$ans;

          #convert  data to JSON
          my $op = JSON -> new -> pretty(1);
          my $json = $op -> encode({result => $res});

          print $cgi->header('application/json;charset=windows-1251');
          print $json;
          ############################################################
          exit;
  }  
  
  #����������� ������ @DAYS � ������, ����� ����� ���� ��� �������� � ��
  my $res_days=join(",", @DAYS);

  #��������� ������ � ������� lessons
  $sql2="insert into lessons (GROUP_ID, TEACHER_ID, ROOM_ID, START_COURSE, END_COURSE, UUID, DAYS_OF_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,NOW())";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2], $form_fields[0], $form_fields[1], $row_data[0], $row_data[1], $row_uuid[0], $res_days, $us_id);
  
  #������� ������� ��� ������ � ��������� ����������� � ������ ������, ����� �������� ������� �������� ������ �� ����. ���� ����������� �� ���� ������ �������, ������� ����������� ��� �������� �������.
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
             $sth2->execute($dt_beg, $dt_end, "�������. �������������:  ".$row_teacher[0], $row_uuid[0], $us_id);
             
             #��������� ������ ��� ������ �������
             $sql2="insert into lessons_list (WEEK_DAY, DATE_LESSON, TIME_BEGIN, TIME_END, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?, NOW())";
             $sth2=$dbh2->prepare($sql2);
             $sth2->execute($DAYS[$ind], $dt_beg, $DAYS[$ind+1], $DAYS[$ind+2], $row_uuid[0], $us_id);

             #��������� ������ � ������ ��������� ��������� ����������� � ������ ������
             foreach my $num_dg (@row_dogovors)
             {             
                $sql2="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
                $sth2=$dbh2->prepare($sql2);
                $sth2->execute($dt_beg, $dt_end, "�������. �������������:  ".$row_teacher[0], $num_dg, $form_fields[2], $row_uuid[0], $us_id);
             }
             
       } 
  
    }  
  }   
  
#����������� ������ @calend_of_lessons � ������, ����� ����� ���� ��� �������� � ��  
my $cal_less=join(",", @calend_of_lessons);
#��������� ������ � ������ ������� ��� � ������� �������. ��� ��� ����, ����� ��� �������� �������� ������ ��������� ����.  
my $sql2="update lessons set ALL_LESSONS=? where UUID=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($cal_less, $row_uuid[0]);


 #������������ ���-�� ������� ����� ������.
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
  
  #��������� ��������� ������ � ����� ����� ������� ����� ��������� ����� �� ���-�� �������.
  my $pay_per_month=$row_data[2]/$cnt_month;
  
  
  #������� ���������� �������� ����� ��� ��������� ����������� � ������ ������.
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
     
     #��������� ������ � ������ ��������� ����������� � ������ ������
     foreach my $num_dg (@row_dogovors)
     {             
        #��������� ������ � ������ ��������� ����������� � ������ ������
		$sql2="insert into pays (PUPILS_NUM_DOGOVOR, PERIOD, SUMM_4_OPL, OPL_SUMM, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,'0',?,?, NOW())";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($num_dg, $period, $pay_per_month, $form_fields[2], $us_id);
		
		#��������� ������ � ��������� ��������� ����������� � ������ ������
        $sql2="insert into visits (PUPILS_NUM_DOGOVOR, PERIOD, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,?, NOW())";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($num_dg, $period, $form_fields[2], $us_id);
     }     
     
  }
    
  $dbh2->commit; #���������� ����������
  $dbh2->{AutoCommit}=1; 
  $dbh2->{RaiseError}=0;
  };
  if ($@) # ���� ��������� ������, �� ���������� ����������
  {
  # ����� ������ eval, ����� ������ ������ �� ������� � ���������� ������ ��������
  eval { $dbh2->rollback; };
  }
  else
  {
    my $ans="������� ��������� �������!"; 
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
   my $ans="���������� ������� ������� ��� ������ ��� ������ ���� � ������� �������!";
   #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
   my $res=$ans;

   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});

   print $cgi->header('application/json;charset=windows-1251');
   print $json;
   exit;
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
