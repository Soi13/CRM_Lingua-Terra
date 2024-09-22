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

my $from=param('from');
my $to=param('to');
my $id_gr=param('id_gr');

$from=~s/\0//g; $from=~s/\.\.//g; $from=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$to=~s/\0//g; $to=~s/\.\.//g; $to=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$id_gr=~s/\0//g; $id_gr=~s/\.\.//g; $id_gr=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;


my $cgi=CGI->new;
my @res;

my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

#my $sql="select lessons_group.ID as 'id', lessons_group.TEXT_MESSAGE as 'text', lessons_group.START_DATE as 'start_date', lessons_group.END_DATE as 'end_date', lessons_group.DETAILS as 'details' from lessons_group, lessons, groups where lessons_group.UUID_LESSONS=lessons.UUID and lessons.GROUP_ID=? and START_DATE between ? and ? and END_DATE between ? and ?";
my $sql="select lessons_group.ID as 'id', lessons_group.TEXT_MESSAGE as 'text', lessons_group.START_DATE as 'start_date', lessons_group.END_DATE as 'end_date', lessons_group.DETAILS as 'details' from lessons_group, lessons, groups where lessons_group.UUID_LESSONS=lessons.UUID and lessons.GROUP_ID=?";

$sth=$dbh->prepare($sql);
#$sth->execute($id_gr,$from, $to, $from, $to);
$sth->execute($id_gr);

while ($data=$sth->fetchrow_hashref) {
push @res, $data;
}


$dbh->disconnect;

my $op=JSON->new->pretty(1);
my $json=$op->encode(\@res);

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