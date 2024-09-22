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
my $able_set_begin=$sess->param('able_set_begin_study');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

   if ($able_set_begin==1) #������� ����� �� ���������� ������������ ������� ������. ��������� ��� �� ���������� ����������� �� ������.
   {
        my $id=param('id_st');
        my $date=param('DATE_ST_BEG');
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $date=~s/\0//g; $date=~s/\.\.//g; $date=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        ########�������� �� ���� ���� ������ ��������
        if (length($date)==0)
        {
           my $ans="���������� ��������� \"���� ������ ��������\"!";
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
        
        #�������� ������������ ����
        ## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
        if ($date!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
        {
           my $ans="��������� ���� ������ �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
        $date=~/(?<=-)(\d{2})(?=-)/;
        if ($&>12)
        {
           my $ans="� ��������� ���� �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
        $date=~/\d{4}/;
        if ($&>3000)
        {
           my $ans="� ��������� ���� �� ������� ������� ���.";
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
        $date=~/(?<=-)(\d{2})$/;
        if ($&>31)
        {
           my $ans="� ��������� ���� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
           #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
           my $res=$ans;

           #convert  data to JSON
           my $op = JSON -> new -> pretty(1);
           my $json = $op -> encode({result => $res});

           print $cgi->header('application/json;charset=windows-1251');
           print $json;
           exit;
        }
        ############################################################################################################################################        
        
                
        #��������� ���� ������ ��������
        my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update groups_students set BEGIN_STUDY=? where ID=?";
        $sth2=$dbh2->prepare($sql2); #��� �������� ������� �� ���������� ��������
        $sth2->execute($date, $id);             
        $dbh2->disconnect;
   
        my $ans="���� ����������� �������!";
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
        my $ans="�� �� ������ ����� ������������� ����� ������ ��������� � ���������!";
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
