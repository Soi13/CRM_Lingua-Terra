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
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $teacher_id=$sess->param('teacher_id');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $cgi=CGI->new;
my @res;

$teacher_id=~s/\0//g; $teacher_id=~s/\.\.//g; $teacher_id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="SELECT pupils.FIO, pupils.DATE_OF_BORN from pupils where day(DATE_OF_BORN)=day(now()) and month(DATE_OF_BORN)=month(now()) and pupils.Num_dogovor in (select pupils.Num_dogovor from pupils, pays, lessons where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=? group by pupils.Num_dogovor) order by pupils.FIO";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id);


print "Content-type: text/html\n\n";

while ($data=$sth->fetchrow_hashref) {
Encode::from_to($data->{"FIO"}, 'windows-1251', 'utf8');
print qq(<p style=" line-height: 1.5;">$data->{"FIO"} - $data->{"DATE_OF_BORN"}</p>);
}


$dbh->disconnect;

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
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
else { print "Location: http://teachers.localhost:6080\n\n"; }

__END__