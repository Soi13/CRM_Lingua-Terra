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
use POSIX;

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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $cgi=CGI->new;
my @array_groups;
my @data;

my $nm_gr=param('nm_gr');
my $page_size=param('page_size');

$nm_gr=~s/\0//g; $nm_gr=~s/\.\.//g; $nm_gr=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$page_size=~s/\0//g; $page_size=~s/\.\.//g; $page_size=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($nm_gr,'utf8','windows-1251'); 

#���������� ������������ ������ � ��������� �����
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
#my $sql="select GROUP_NAME from groups order by GROUP_NAME";
my $sql="select ID from groups order by GROUP_NAME";
$sth=$dbh->prepare($sql);
$sth->execute();

#���������� ��� � ������
while (@data=$sth->fetchrow_array) {
push @array_groups, @data;
}

my $cnt_tmp=0;
my $cnt=0;

for (my $g=0; $g<=$#array_groups; $g++)
{
    my $curr_gr=$array_groups[$g];
    $cnt_tmp++;    
    if ($curr_gr eq $nm_gr)
    {
      $cnt=$cnt_tmp/$page_size;
      last;    
    }           
}


my $op=JSON->new->pretty(1);
my $json=$op->encode({result => ceil($cnt)});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;


#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://linguaterra-soft.ru');
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