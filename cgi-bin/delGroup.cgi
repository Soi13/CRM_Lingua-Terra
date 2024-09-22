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
use REST::Client;


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
my $able_del_group=$sess->param('able_del_group');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

   if ($able_del_group==1) #������� ����� �� ���������� ������������ ������� ������. ��������� ��� �� ���������� ����������� �� ������.
   {
        my $id=param('id_gr');
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        #######################�������, ��������� �� � ������ ��������, ���� ���������, �� ������� ������!###########################
        my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select GROUP_ID from groups_students where GROUP_ID=?";
        $sth=$dbh->prepare($sql);
        $sth->execute($id);
        #� ������ ���������� ����������� ������
        my @row_stud = $sth->fetchrow_array;
        $dbh->disconnect;        
        if (@row_stud)
        {
            my $ans="� ������ ��������� ��������, ������� ������ ����������!";
            #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
            my $res=$ans;

            #convert  data to JSON
            my $op = JSON -> new -> pretty(1);
            my $json = $op -> encode({result => $res});

            print $cgi->header('application/json;charset=windows-1251');
            print $json;
            exit;
        }
        ###############################################################################################################################
        
        
        #######################�������, ������� �� ��� ������ �������, ���� ��, �� ������� ������!#####################################
        my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        my $sql1="select GROUP_ID from lessons where GROUP_ID=?";
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($id);
        #� ������ ���������� ����������� ������
        my @row_less = $sth1->fetchrow_array;
        $dbh1->disconnect;        
        if (@row_less)
        {
            my $ans="� ������ ��������� �������, ������� ������ ����������!";
            #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
            my $res=$ans;

            #convert  data to JSON
            my $op = JSON -> new -> pretty(1);
            my $json = $op -> encode({result => $res});

            print $cgi->header('application/json;charset=windows-1251');
            print $json;
            exit;
        }
        ###############################################################################################################################
        
		#�������� ������� ������������ ������ ����� ��� ���������������.
        my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth3=$dbh3->do("SET NAMES 'cp1251'");
        my $sql3="select GROUP_NAME from `groups` where ID=?";
        $sth3=$dbh3->prepare($sql3);
        $sth3->execute($id);
        #� ������ ���������� ����������� ������
        my @row_gr_name = $sth3->fetchrow_array;
                
        #���� ������� � �������� �� ���������, �� ������� ������
        my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="delete from groups where ID=?";
        $sth2=$dbh2->prepare($sql2); #��� �������� ������� �� ���������� ��������
        $sth2->execute($id);  
        $dbh2->disconnect;
		
		#######���������� ������ ��� ������ � REST ��������� ��� ������� � ������ ������
        #������������ � ������ � �������� SID, ����� � ���������� � ������� ���� ��������� ����� ������
        my $client_rest = REST::Client->new();
        $client_rest->GET('http://46.180.119.231:5533/webapi/auth.cgi?api=SYNO.API.Auth&version=3&method=login&account=LinguaPlatform&passwd=Lingua2021!&session=FileStation&format=sid');
        my $res_json = JSON->new->utf8->decode($client_rest->responseContent());
        my $sid_cloud=$res_json->{'data'}->{'sid'};
  
        #������� ����� �� ������
        my $client_folder = REST::Client->new();
        $client_folder->GET('http://46.180.119.231:5533/webapi/entry.cgi?api=SYNO.FileStation.Delete&version=1&method=delete&path=%22%2FLinguaPlatform%2F'.$row_gr_name[0].'%22&_sid='.$sid_cloud);
        $client_folder->responseContent();

        my $ans="������ ������� �������!";
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
        my $ans="�� �� ������ ����� ������� ������!";
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
