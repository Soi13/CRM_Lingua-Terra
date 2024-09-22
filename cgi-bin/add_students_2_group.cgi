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

my @data=param('dat');

#��������� ������� �� �������� ��� ��������. ���� �� �������, �� ������ ������� 1, �.�. � ���� � ����� ������ ���������� ID ������
if (scalar(@data)==1)
{
  my $ans="�� ������� �������� ��� �������� � ������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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

  #��������� �������� �� ������� � ������. ���� ��, �� ��� ���� �������� �� ��������, �.�. ������������� ��������� � ���� ������� ���� � ��� �� ������� �� �����. ���������� ������� ��� ���.������� ��� ����� ��������.
  for (my $n_dg=1; $n_dg<=$#data; $n_dg++)    
  {
     my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
     my $sth5=$dbh5->do("SET NAMES 'cp1251'");
     my $sql5="select groups_students.PUPILS_NUM_DOGOVOR, pupils.FIO from groups_students, pupils where groups_students.PUPILS_NUM_DOGOVOR=pupils.Num_dogovor and groups_students.PUPILS_NUM_DOGOVOR=?";
     $sth5=$dbh5->prepare($sql5);
     $sth5->execute($data[$n_dg]);
     #� ������ ���������� ����������� ������
     my @stud = $sth5->fetchrow_array;
     if (@stud)
     {
         my$ans="������� <b>".$stud[1]."</b> ��� �������� � ������. ������������� ���������� ����� � ��� ����� ������ ����������! ������� ������� �������� �� ������ ������������� � ��������� ��������.";
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
  }

#����������, ���� �� ��������� ������� ��� ������ ������? ���� ����, �� ����������� �������� � ������ � ����� ����������� �� � ��������� ��� �������, ���� ������� ���, �� ������ ����������� ��������� � ������
  my $dbh0=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth0=$dbh0->do("SET NAMES 'cp1251'");
  my $sql0="select GROUP_ID, START_COURSE, END_COURSE, UUID, DAYS_OF_LESSONS, TEACHER_ID, ALL_LESSONS from lessons where GROUP_ID=?";
  $sth0=$dbh0->prepare($sql0); #��� �������� ������� �� ���������� ��������
  $sth0->execute($data[0]);  
  my @row_data = $sth0->fetchrow_array;
  $dbh0->disconnect;
  if (@row_data)
  {
    
    #�������� ������ ��������� ����� �� ������ �� ID ������ ����������� � �����
    my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
    my $sth4=$dbh4->do("SET NAMES 'cp1251'");
    my $sql4="select COURSE_PRICE from groups where ID=?";
    $sth4=$dbh4->prepare($sql4);
    $sth4->execute($data[0]);
    #� ������ ���������� ����������� ������
    my @row_price = $sth4->fetchrow_array;

    my $dbh1=DBI->connect("DBI:mysql:a0018982_fin", "a0018982_oleg", "LinguaTerra2016", {RaiseError => 1, AutoCommit => 0}) or die "Error: $DBI::errstr\n";
    my $sth1=$dbh1->do("SET NAMES 'cp1251'");
    eval {

    #����������� ��������� � ������  
    for (my $t=1; $t<=$#data; $t++)
    {
      my $sql1="insert into groups_students (GROUP_ID, PUPILS_NUM_DOGOVOR, USER_ID, DATETIME_CREATE, PRICE_COURSE) values (?,?,?, NOW(),?)";
      $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
      $sth1->execute($data[0], $data[$t], $us_id, $row_price[0]);
    } 
    #####################################

    #��������������� ������ ���������� �� DAYS_OF_LESSONS � ������
    my @day_time_data=split(",", $row_data[4]);

    #�������� ��� ������� �� ID ����������� � �����
    my $sql1="select FIO from teachers where ID=?";
    $sth1=$dbh1->prepare($sql1);
    $sth1->execute($row_data[5]);
    #� ������ ���������� ����������� ������
    my @row_teacher = $sth1->fetchrow_array;
    ################################################ 
        

=head		
    #����� �� ��������� ��� ��������, ���� ��������� ��� � ��������� �� � ����� � ��������� ��������
    my $first = $row_data[1];
    my $second = $row_data[2];  
    my @f = ($first =~ /^(\d+)\-(\d+)\-(\d+)$/);
    my @s = ($second =~ /^(\d+)\-(\d+)\-(\d+)$/);
    my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
    my $sepoch = timelocal(0,0,0,$s[2],$s[1]-1,$s[0]);
    ($fepoch,$sepoch) = ($sepoch,$fepoch) if $fepoch > $sepoch;
    for (my $ind=0; $ind<=$#day_time_data; $ind=$ind+3)
    {
      for (my $i=$fepoch; $i <= $sepoch; $i += 24 * 60 * 60)
      {
       #print scalar localtime($i),"\n";
       my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($i);
       $year=$year+1900;
       #print $mday.".".($mon+1)."    ".$wday,  "\n" if ($wday==1 || $wday==3);     
       if ($wday==$day_time_data[$ind])
       {
             my $dt_beg=$year."-".($mon+1)."-".$mday." ".$day_time_data[$ind+1];
             my $dt_end=$year."-".($mon+1)."-".$mday." ".$day_time_data[$ind+2];                         
             
             #��������� ������ � ������ ��������� ��������� ����������� � ������ ������
             for (my $t0=1; $t0<=$#data; $t0++)
             { 
                my $sql1="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
                $sth1=$dbh1->prepare($sql1);
                $sth1->execute($dt_beg, $dt_end, "�������. �������������:  ".$row_teacher[0], $data[$t0], $data[0], $row_data[3], $us_id);
             }
             
             
        }
      
      }  
    }
=cut

    #��������������� ������ ���������� �� DAYS_OF_LESSONS � ������
    my @full_day_time_data=split(",", $row_data[6]);
    
    #��������� ������ � ������ ��������� ��������� ����������� � ������ ������
    for (my $t0=1; $t0<=$#data; $t0++)
    { 
      for (my $t9=0; $t9<=$#full_day_time_data; $t9=$t9+3)
      {  
        my $sql1="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($full_day_time_data[$t9]." ".$full_day_time_data[$t9+1], $full_day_time_data[$t9]." ".$full_day_time_data[$t9+2], "�������. �������������:  ".$row_teacher[0], $data[$t0], $data[0], $row_data[3], $us_id);
      }
    }
        

     #������������ ���-�� ������� ����� ������.
     my $first_dt = $row_data[1];
     my $second_dt = $row_data[2];
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
     my $pay_per_month=$row_price[0]/$cnt_month;
  
     #������� ���������� �������� ����� ��� ��������� ����������� � ������ ������.
     my $first_date = $row_data[1];
     my $second_date = $row_data[2];
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
       for (my $t4=1; $t4<=$#data; $t4++)       
       {             
          my $sql1="insert into pays (PUPILS_NUM_DOGOVOR, PERIOD, SUMM_4_OPL, OPL_SUMM, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?, NOW())";
          $sth1=$dbh1->prepare($sql1);
          $sth1->execute($data[$t4], $period, $pay_per_month, '0', $data[0], $us_id);
		  
		  #��������� ������ � ��������� ��������� ����������� � ������ ������
          my $sql1="insert into visits (PUPILS_NUM_DOGOVOR, PERIOD, GROUP_ID, USER_ID, DATETIME_CREATE) values (?,?,?,?, NOW())";
          $sth1=$dbh1->prepare($sql1);
          $sth1->execute($data[$t4], $period, $data[0], $us_id);
       }     
     
     }
     
     $dbh1->commit; #���������� ����������
     $dbh1->{AutoCommit}=1; 
     $dbh1->{RaiseError}=0;
     };
     if ($@) # ���� ��������� ������, �� ���������� ����������
     {
     # ����� ������ eval, ����� ������ ������ �� ������� � ���������� ������ ��������
     eval { $dbh1->rollback; };
     }
     else
    {

     if ($#data>1)
     {
      my$ans="�������� ��������� ������!";
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
      my$ans="������� �������� ������!";
      #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
      my $res=$ans;

      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});

      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      ############################################################  
     }
      
     exit;
  
    } 

  }
  else
  {
  
  #�������� ������ ��������� ����� �� ������ �� ID ������ ����������� � �����
  my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth4=$dbh4->do("SET NAMES 'cp1251'");
  my $sql4="select COURSE_PRICE from groups where ID=?";
  $sth4=$dbh4->prepare($sql4);
  $sth4->execute($data[0]);
  #� ������ ���������� ����������� ������
  my @row_price1 = $sth4->fetchrow_array;

  #����������� ��������� � ������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  for (my $t=1; $t<=$#data; $t++)
  {
    my $sql1="insert into groups_students (GROUP_ID, PUPILS_NUM_DOGOVOR, USER_ID, DATETIME_CREATE, PRICE_COURSE) values (?,?,?, NOW(),?)";
    $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
    $sth1->execute($data[0], $data[$t], $us_id, $row_price1[0]);
  } 
   
  if ($#data>1)
  {
    my$ans="�������� ��������� ������!";
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
    my$ans="������� �������� ������!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    ############################################################  
  }
   $dbh1->disconnect;
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
