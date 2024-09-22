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
my $able_change_summ=$sess->param('able_change_summ_4_opl');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

   if ($able_change_summ==1) #������� ����� �� ���������� ������������ �������� ����� � ������. ��������� ��� �� ���������� ����������� �� ������.
   {
        my $id=param('id_pay');
        my $new_summ=param('CHANGE_SUM_PAY');   
        my $num_dog=param('num_dogovor_stud');                        
        $id=~s/\0//g; $id=~s/\.\.//g; $id=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $new_summ=~s/\0//g; $new_summ=~s/\.\.//g; $new_summ=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $num_dog=~s/\0//g; $num_dog=~s/\.\.//g; $num_dog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        
        ########�������� �� ���� ����� ������
        if (length($new_summ)==0)
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
        if ($new_summ!~m/^\s*\d+\.\d+\s*$/is)
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
        
        #######################�������� ����� �������� �������� � ID ������ �� ID �� ������� pays###########################
        my $dbh0=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth0=$dbh0->do("SET NAMES 'cp1251'");
        my $sql0="select PUPILS_NUM_DOGOVOR, GROUP_ID from pays where ID=?";
        $sth0=$dbh0->prepare($sql0);
        $sth0->execute($id);
        #� ������ ���������� ����������� ������
        my @row_num_dog = $sth0->fetchrow_array;
                
        
        #######################���������� �������������� ����� �������###########################
        my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="update pays set SUMM_4_OPL=? where ID=?";
        $sth=$dbh->prepare($sql);
        $sth->execute($new_summ, $id);
              
        
        #######################�������� �����, ���������� ����� ��������������, ��������� ����� �������� �� ������ �������� � ID ������ �� ������� pays###########################
        my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        my $sql1="select sum(SUMM_4_OPL) from pays where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($row_num_dog[0], $row_num_dog[1]);
        #� ������ ���������� ����������� ������
        my @row_new_price_course = $sth1->fetchrow_array;
        
        
        #######################���������� �������������� ��������� ����� ����������� � �������� � ������� groups_students. ��� ���� ������ �.�. ���� �������������� ����� ������� � ����� ����� ����� ����������###########################
        my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update groups_students set PRICE_COURSE=? where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth2=$dbh2->prepare($sql2);
        $sth2->execute($row_new_price_course[0], $row_num_dog[0], $row_num_dog[1]);
        
        
        ##############���� ������������� ���������� ���� ����� �������� ������������� ��������� � ������ ��� �����######################
        my @row;
        my @data;

        my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth3=$dbh3->do("SET NAMES 'cp1251'");
        my $sql3="select ID, SUMM_4_OPL, OPL_SUMM from pays where PUPILS_NUM_DOGOVOR=? and GROUP_ID=?";
        $sth3=$dbh3->prepare($sql3);
        $sth3->execute($row_num_dog[0], $row_num_dog[1]);

        while (@data=$sth3->fetchrow_array) {
        push @row, @data;
        }
        $dbh3->disconnect;

        my $res;
        my $res_nedoplata;
        my $pereplata;
        my $nedoplata;

       for (my $i=0; $i<=$#row; $i=$i+3)
       {
         #���� ����� � ������ � ���������� ����� �����
         if ($row[$i+2]==$row[$i+1])
         {
            next;    
         } 
   
         #���� ���������� ����� ������ ����� � ������  
         if ($row[$i+2]>$row[$i+1])
         {     
            $pereplata=$row[$i+2]-$row[$i+1];
            $res=$row[$i+2]-$pereplata; 
     
            my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
            my $sth4=$dbh4->do("SET NAMES 'cp1251'");
          
            #������ ���������� ����� � ������� ������
            my $sql4="update pays set OPL_SUMM=? where ID=?";
            $sth4=$dbh4->prepare($sql4);
            $sth4->execute($res, $row[$i]);     
     
            $row[$i+2]=$res;
     
            #������ ����� �����������, ��������� �� ������� �������
            my $sql4="update pays set OPL_SUMM=OPL_SUMM+? where ID=?";
            $sth4=$dbh4->prepare($sql4);
            $sth4->execute($pereplata, $row[$i+3]);
     
            $row[$i+5]=$row[$i+5]+$pereplata;
         }
   
   
         #���� ���������� ����� ������ ����� � ������
         if ($row[$i+2]<$row[$i+1])
         {     
            $nedoplata=$row[$i+1]-$row[$i+2];
     
            if ($row[$i+5]>=$nedoplata)
            { 
               $res_nedoplata=$row[$i+5]-$nedoplata;
       
               #������ ��������� � ������� ������
               my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
               my $sth5=$dbh5->do("SET NAMES 'cp1251'");
               my $sql5="update pays set OPL_SUMM=OPL_SUMM+? where ID=?";
               $sth5=$dbh5->prepare($sql5);
               $sth5->execute($nedoplata, $row[$i]);
        
               $row[$i+2]=$row[$i+2]+$nedoplata;
                
               #������ ����� � ��������� ������, �.�. �� �� ���� ����� ����� ����� ���������
               my $dbh6=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
               my $sth6=$dbh6->do("SET NAMES 'cp1251'");
               my $sql6="update pays set OPL_SUMM=? where ID=?";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute($res_nedoplata, $row[$i+3]);
        
               $row[$i+5]=$res_nedoplata;
			   next;
            
            }
			
			if (($row[$i+5]<$nedoplata) && ($row[$i+5]!=0))            
            { 
               #$res_nedoplata=$row[$i+5]-$nedoplata;
       
               #������ ��������� � ������� ������
               my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
               my $sth5=$dbh5->do("SET NAMES 'cp1251'");
               my $sql5="update pays set OPL_SUMM=OPL_SUMM+? where ID=?";
               $sth5=$dbh5->prepare($sql5);
               $sth5->execute($row[$i+5], $row[$i]);
        
               $row[$i+2]=$row[$i+2]+$row[$i+5];
                
               #������ ����� � ��������� ������, �.�. �� �� ���� ����� ����� ����� ���������
               my $dbh6=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
               my $sth6=$dbh6->do("SET NAMES 'cp1251'");
               my $sql6="update pays set OPL_SUMM=? where ID=?";
               $sth6=$dbh6->prepare($sql6);
               $sth6->execute("0", $row[$i+3]);
        
               $row[$i+5]=0;
               next;
            }
     
         }
      }
      #################################################################################################################################
        
        
        $dbh0->disconnect;       
        $dbh->disconnect;
        $dbh1->disconnect;
        $dbh2->disconnect;
		
		#������������� Null �������� � ���� IS_MOVED. ��� �������� ��� ����, ����� ������ ������� � �������� � ������ ��� �������� �� ������ � ������.
        my $dbh7=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth7=$dbh7->do("SET NAMES 'cp1251'");
        my $sql7="update pupils set IS_MOVED=Null where num_dogovor=?";
        $sth7=$dbh7->prepare($sql7);
        $sth7->execute($num_dog);
    
        my $ans="����� �������� �������!";
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
        my $ans="�� �� ������ ����� �������� ����� ��� ������!";
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
