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

#�������� ������ �� �������� ��� ��������������
my @LESSONS_4_EDIT=param('LESSONS_4_EDIT');

if (@LESSONS_4_EDIT)
{
  #��������� � ������� ������ �� ������ �����
  for (my $g=0; $g<=$#LESSONS_4_EDIT; $g++)
  {
        $LESSONS_4_EDIT[$g]=~s/\0//g;
        $LESSONS_4_EDIT[$g]=~s/\.\.//g;
        $LESSONS_4_EDIT[$g]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;        
  }
  ############# 
  
  ###���������, ��� �� ���� �� �������� ���������.
  for (my $u=0; $u<=$#LESSONS_4_EDIT; $u++)
  {        
        if (($LESSONS_4_EDIT[$u] eq '') || ($LESSONS_4_EDIT[$u] eq ' '))
        {
                my $ans="�� ��������� ��������� ���������� � ��������!";
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

  ##���������, ��������� �� ������� ���� ������� �� ������� �� ���� ���� ������ �����)))
  for (my $u1=0; $u1<=$#LESSONS_4_EDIT; $u1=$u1+4)
  {
        ## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
        if ($LESSONS_4_EDIT[$u1]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
        {
                my $ans="��������� ���� ������� �� ���������. ������ ������ ����, ��������, 2016-05-30";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        ###########################################################################################################################################
        # ��������� ���� �� ���� ����� � ��� � ��������� ����� ����� ���� �� ��������� �����������. �������� ����� �� ����� ���� ������ 12, ���� 31
        ###########################################################################################################################################
        
        # ��������� ����� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
        $LESSONS_4_EDIT[$u1]=~/(?<=-)(\d{2})(?=-)/;
        if ($&>12)
        {
                my $ans="� ��������� ���� ������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        # ��������� ��� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
        $LESSONS_4_EDIT[$u1]=~/\d{4}/;
        if ($&>3000)
        {
                my $ans="� ��������� ���� ������� �� ������� ������� ���.";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        # ��������� ���� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
        $LESSONS_4_EDIT[$u1]=~/(?<=-)(\d{2})$/;
        if ($&>31)
        {
                my $ans="� ��������� ���� ������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
                #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
                my $res=$ans;

                #convert  data to JSON
                my $op = JSON -> new -> pretty(1);
                my $json = $op -> encode({result => $res});

                print $cgi->header('application/json;charset=windows-1251');
                print $json;
                exit;
        }
        
        
        ########��������� ���, ����� ������������ �������� �� ���� ���� ������� ������ ���� ������ ����� � ������ ���� ��������� �����
        my @f = ($start_date =~ /^(\d+)\-(\d+)\-(\d+)$/);
        my @e = ($LESSONS_4_EDIT[$u1] =~ /^(\d+)\-(\d+)\-(\d+)$/);
        my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
        my $sepoch = timelocal(0,0,0,$e[2],$e[1]-1,$e[0]);
        if ($fepoch>$sepoch)
        {
          my $ans="��������� ���� ������� ������ ���� ������ �����!";
          #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
          my $ans="��������� ���� ������� ������ ���� ��������� �����!";
          #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
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
  

  ##���������, ��������� �� ������� ����� �������? �� ������� �� ���� ���� ������ �����)))
  for (my $u2=1; $u2<=$#LESSONS_4_EDIT; $u2=$u2+4)
  {
        #��������� ������ ������� �������, �.�. �� �������� ��������� ���� �������, � ����� ������, ����� ����������� �������� � ������� �������
        if ($LESSONS_4_EDIT[$u2]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
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
        
        if ($LESSONS_4_EDIT[$u2+1]!~m/^([0-1]\d|2[0-3])(:[0-5]\d)$/is)
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

  }
=head  
  ##���������, ����� ����� ������ ������� �� ���� ������ ��������� �������
  for (my $u3=1; $u3<=$#LESSONS_4_EDIT; $u3=$u3+4)
  {
        
        #���������, ����� ����� ������ ������� �� ���� ������ ��������� �������
        my $t1 = $LESSONS_4_EDIT[$u3];
        my $t2 = $LESSONS_4_EDIT[$u3+1];

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
        
        my $time1= undef;
        my $time2= undef;
  }
=cut
}

#�������� ������ ��������� ���� ��������� ����������� � ������, ����� ������������ �� ������ ��������� �������
my $data4;
my @row_dogovors;
my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="select PUPILS_NUM_DOGOVOR from groups_students where GROUP_ID=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($idd_gr);
#� ������ ���������� ����������� ������
while ($data4=$sth4->fetchrow_array) {
push  @row_dogovors, $data4;
}
$dbh4->disconnect;
################################################


#�������� ��� ������� �� ID ����������� � �����
my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth5=$dbh5->do("SET NAMES 'cp1251'");
my $sql5="select FIO from teachers where ID=?";
$sth5=$dbh5->prepare($sql5);
$sth5->execute($teach_id);
#� ������ ���������� ����������� ������
my @row_teacher = $sth5->fetchrow_array;
$dbh5->disconnect;
################################################


#���������� UUID ������� ������������ � ������
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select UUID from lessons where GROUP_ID=?";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($idd_gr);
#� ������ ���������� ����������� ������
my @row_uuid = $sth1->fetchrow_array;
$dbh1->disconnect;
################################################
 

#��������� ������ �� ������� � ������� ������� 
my $dbh0=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth0=$dbh0->do("SET NAMES 'cp1251'");
my $sql0="update lessons set TEACHER_ID=?, ROOM_ID=? where GROUP_ID=?";
$sth0=$dbh0->prepare($sql0);
$sth0->execute($teach_id, $room_id, $idd_gr);
$dbh0->disconnect;
################################################


#���� �� ������� � ���������� �������������� �������
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
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

#������� ������ �� UUID �� ������� lessons_group (��������� ������), ����� ����� �������� �����. ����� ������� ���������� ����������, �.� update ������� ����� �� ����������
my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="delete from lessons_group where UUID_LESSONS=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($row_uuid[0]);
$dbh2->disconnect;
################################################

#������� ������ �� UUID �� ������� calendar_pupils (��������� ��������), ����� ����� �������� �����. ����� ������� ���������� ����������, �.� update ������� ����� �� ����������
my $dbh6=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth6=$dbh6->do("SET NAMES 'cp1251'");
my $sql6="delete from calendar_pupils where UUID_LESSONS=?";
$sth6=$dbh6->prepare($sql6);
$sth6->execute($row_uuid[0]);
$dbh6->disconnect;
################################################


#���� �� ������� � ���������� ������� ������� � ������� lessons_group
my @calend_of_lessons;  
my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
for (my $g2=0; $g2<=$#LESSONS_4_EDIT; $g2=$g2+4)
{
   #my @f = ($LESSONS_4_EDIT[$g2] =~ /^(\d+)\-(\d+)\-(\d+)$/);
   #my $days = Day_of_Week($f[0],$f[1],$f[2]);
   #$days=0 if ($days==7);
   
   my $sql3="insert into lessons_group (START_DATE, END_DATE, TEXT_MESSAGE, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?, NOW())";
   $sth3=$dbh3->prepare($sql3);
   $sth3->execute($LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+1], $LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+2], "�������. �������������:  ".$row_teacher[0], $row_uuid[0], $us_id);
   
   push @calend_of_lessons, $LESSONS_4_EDIT[$g2], $LESSONS_4_EDIT[$g2+1], $LESSONS_4_EDIT[$g2+2];
   
   #��������� ������ � ������ ��������� ��������� ����������� � ������ ������
   foreach my $num_dg (@row_dogovors)
   {             
    $sql3="insert into calendar_pupils (START_DATE, END_DATE, TEXT_MESSAGE, PUPILS_NUM_DOGOVOR, GROUP_ID, UUID_LESSONS, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?, NOW())";
    $sth3=$dbh3->prepare($sql3);
    $sth3->execute($LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+1], $LESSONS_4_EDIT[$g2]." ".$LESSONS_4_EDIT[$g2+2], "�������. �������������:  ".$row_teacher[0], $num_dg, $idd_gr, $row_uuid[0], $us_id);
   } 
   
}
$dbh3->disconnect;

#����������� ������ @calend_of_lessons � ������, ����� ����� ���� ��� �������� � ��  
my $cal_less=join(",", @calend_of_lessons);

##��������� ������ � ������ ������� ��� � ������� �������. ��� ��� ����, ����� ��� �������� �������� ������ ��������� ����.
my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="update lessons set ALL_LESSONS=? where UUID=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($cal_less, $row_uuid[0]);
$dbh4->disconnect;


my $res1="������� ��������������� �������!";
my $op1=JSON->new->pretty(1);
my $json1=$op1->encode({result => $res1});
#my $json=$op->encode(\@res);
print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json1;


#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
#         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
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