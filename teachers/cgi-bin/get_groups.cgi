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

my $page=param('page');
my $rows=param('rows');
my $sort=param('sort');
my $order=param('order');
my $group=param('group');
my $language=param('language');
my $level_knowledge=param('level_knowledge');
my $kind_programm=param('kind_programm');
my $group_type=param('group_type');
my $type_calc_lesson=param('type_calc_lesson');
my $count_classes=param('count_classes');
my $duration_classes=param('duration_classes');
my $course_price=param('course_price');
my $type_pay=param('type_pay');
my $branch=param('branch');
my $room=param('room');
my $erase_filter=param('erase_filter');
my $naim_gr=param('naim_gr');
my $status=param('status');

$group=~s/\0//g; $group=~s/\.\.//g; $group=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$language=~s/\0//g; $language=~s/\.\.//g; $language=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$level_knowledge=~s/\0//g; $level_knowledge=~s/\.\.//g; $level_knowledge=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$kind_programm=~s/\0//g; $kind_programm=~s/\.\.//g; $kind_programm=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$group_type=~s/\0//g; $group=~s/\.\.//g; $group_type=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$type_calc_lesson=~s/\0//g; $type_calc_lesson=~s/\.\.//g; $type_calc_lesson=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$count_classes=~s/\0//g; $count_classes=~s/\.\.//g; $count_classes=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$duration_classes=~s/\0//g; $duration_classes=~s/\.\.//g; $duration_classes=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$course_price=~s/\0//g; $course_price=~s/\.\.//g; $course_price=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$type_pay=~s/\0//g; $type_pay=~s/\.\.//g; $type_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$branch=~s/\0//g; $branch=~s/\.\.//g; $branch=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$room=~s/\0//g; $room=~s/\.\.//g; $room=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$erase_filter=~s/\0//g; $erase_filter=~s/\.\.//g; $erase_filter=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$teacher_id=~s/\0//g; $teacher_id=~s/\.\.//g; $teacher_id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($group, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)
Encode::from_to($language, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)
Encode::from_to($level_knowledge, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)
Encode::from_to($kind_programm, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)
Encode::from_to($group_type, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)
Encode::from_to($type_calc_lesson, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)
Encode::from_to($type_pay, 'utf-8', 'cp1251'); #���������� ���������������� �� utf8 � cp1251 (Windows-1251)


##################���������� �� "����". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($language) && length($language)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=lessons.GROUP_ID and `lessons`.TEACHER_ID=? and LANGUAGE=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $language);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select groups.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and LANGUAGE=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $language, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################���������� �� "�������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($level_knowledge) && length($level_knowledge)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and LEVEL_KNOWLEDGE=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $level_knowledge);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and LEVEL_KNOWLEDGE=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $level_knowledge, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

##################���������� �� "���������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($kind_programm) && length($kind_programm)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and KIND_PROGRAMM=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $kind_programm);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and KIND_PROGRAMM=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $kind_programm, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

##################���������� �� "��� ������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($group_type) && length($group_type)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and GROUP_TYPE=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $group_type);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select * from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and GROUP_TYPE=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $group_type, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################���������� �� "������ ������� ������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($type_calc_lesson) && length($type_calc_lesson)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and TYPE_CALC_LESSON=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $type_calc_lesson);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select groups.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and TYPE_CALC_LESSON=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $type_calc_lesson, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################���������� �� "���-�� �������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($count_classes) && length($count_classes)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and COUNT_CLASSES=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $count_classes);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and COUNT_CLASSES=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $count_classes, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################���������� �� "����������������� �������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($duration_classes) && length($duration_classes)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and DURATION_CLASSES=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $duration_classes);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and DURATION_CLASSES=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $duration_classes, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################���������� �� "���� �����". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($course_price) && length($course_price)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and COURSE_PRICE like ?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $course_price);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `gropus`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and COURSE_PRICE like ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $course_price, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################


##################���������� �� "��� �������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($type_pay) && length($type_pay)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and TYPE_PAY=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $type_pay);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and TYPE_PAY=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $type_pay, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

##################���������� �� "������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($branch) && length($branch)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and BRANCH=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $branch);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and BRANCH=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $branch, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

##################���������� �� "���������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($room) && length($room)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and `lessons`.ROOM_ID=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, $room);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`,`lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and `lessons`.ROOM_ID=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $room, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

##################���������� �� "����� ��� �������". ���� ������ ���������� ����������, �� ������������� ����������, ���� �� ����������, �� ��������� ����� ������ ������ � ������������ ������
if (defined($erase_filter) && length($erase_filter)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
###########################################################################################

#���� ������ ����������, �������� � ��� �� ����� 0, �� ��������� �����
if (defined($group) && length($group)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and GROUP_NAME like ?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id, '%'.$group.'%');

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;
my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? and GROUP_NAME like ? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, '%'.$group.'%', $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
else #����� ������ �� ����������, �� �������� � ��� ����� 0, �� ���������� ���� ������ �����
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select `groups`.* from `groups`, `lessons` where `groups`.ID=`lessons`.GROUP_ID and `lessons`.TEACHER_ID=? order by $sort $order limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($teacher_id, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}


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