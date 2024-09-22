#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use Build_Menu qw(:DEFAULT $idd);

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
my $days_expired=$sess->param('days_expired_passw');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
        #���������� �������� ����������� ��� ������ �� �� ��������
        open FF, "<txt_data/name_org.txt";
        my @name_org=<FF>;
        foreach my $str (@name_org)
        {
           $str=~s/\0//g;
           $str=~s/\.\.//g;
           $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        }
        close (FF) or die $!;
        #########################################

        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time); 
        $mon=$mon+1;
        $year=$year+1900;

        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@name_org</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxchart.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css">
		<link rel="stylesheet" href="../amcharts/plugins/export/export.css" type="text/css" media="all" />  
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../JS/dhtmlxchart.js"></script>
		<script src="../amcharts/amcharts.js"></script>
        <script src="../amcharts/funnel.js"></script>
        <script src="../amcharts/plugins/export/export.min.js"></script>
        <script src="../amcharts/plugins/dataloader/dataloader.min.js" type="text/javascript"></script>
        <script src="../amcharts/themes/light.js"></script>

        <script>
        var chart = AmCharts.makeChart( "chartdiv", {
        "type": "funnel",
        "theme": "light",
        "dataLoader": {
                        "url": "get_sales_funnel.cgi?SID=$SID",
                        "format": "json"
                      },
        "balloon": {
                 "      fixedPosition": true
                   },
        "valueField": "value",
        "titleField": "title",
        "marginRight": 240,
        "marginLeft": 50,
        "startX": -500,
        "depth3D": 0,
        "angle": 40,
        "outlineAlpha": 1,
        "outlineColor": "#FFFFFF",
        "outlineThickness": 2,
        "labelPosition": "right", 
        "marginTop": 40,  
        "allLabels": [
		      {
			"text": "������� ������ �� ������� ����� ($mon.$year)",
			"bold": true,
			"x": 70,
			"y": 25
		      }
                     ],  
        "balloonText": "[[title]]: [[value]] ��.[[description]]",
        "export": {
                     "enabled": false
                  }
        });
        </script>

		
        <script>
        function confirm1(){
        \$.messager.confirm('��������', '�� �������, ��� ���������� �����', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increae time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("http://localhost:6080")}
                                });  });    </script>

        <script> //�������� ����� ����� ������
        function call() {
        var msg   = \$('#ff').serialize();
        \$.ajax({
          type: 'GET',
          url: 'change_psw.cgi?SID=$SID',
          data: msg,
          success: function(res) {alert(res.result); \$('#ff')[0].reset(); \$('#w').window('close');},
          error: function() {alert("did not work");}
        });

       }
       </script>
       
       <script>
		var myPieChart;	
                                     var myPieChart_age;	
		function doOnLoad() {
		        		        
			myPieChart = new dhtmlXChart({
				view:"pie3D",
				container:"chartbox",
				value:"#count#",
				
				tooltip:"���-��: <b>#count#</b>",
				legend:{
					width: 75,
					align:"right",
					valign:"middle",
					template:"#sex#"
				},
				gradient:1,
				shadow:true,
				
				color:function(obj){
                               if (obj.sex == '�') return "#ff9900";
                               if (obj.sex == '�') return "#66cc00";
                               }
			});
			myPieChart.load("get_sex.cgi?SID=$SID", "json");

            //����� ��������� �� ��������
			myPieChart_age = new dhtmlXChart({
				view:"pie3D",
				container:"chartbox_branch",
				value:"#count#",
				tooltip:"���-�� ���������: <b>#count#</b>",
				legend:{
					width: 200,
					align:"right",
					valign:"middle",
					template:"#BRANCH#"
				},
				gradient:1,
				shadow:true
			});
			myPieChart_age.load("get_branch.cgi?SID=$SID", "json");


            
			//����� ��������� �� ���� ��������/���������� ��������
			myLineChart_date_reg = new dhtmlXChart({
				view:"spline",
				container:"chartbox_date_reg",
				value:"#count#",
				tooltip:"���-�� ����������� ���������: <b>#count#</b>",
				gradient:1,
				shadow:true,
				xAxis:{
                                       title:"����/����� ����������� ��������",
                                       template:"#day#"
                                      },
                                yAxis:{
                                       title:"���-�� �����������"                                       
                                      },
        
			});
			myLineChart_date_reg.load("get_count_reg_students.cgi?SID=$SID", "json");
            
			
            
			//����� ��������� �� ���� �������� ������
			myLineChart_date_zayav = new dhtmlXChart({
				view:"spline",
				container:"chartbox_date_zayav",
				value:"#count#",
				tooltip:"���-�� �������� ������: <b>#count#</b>",
				gradient:1,
				shadow:true,
				xAxis:{
                                       title:"����/����� �������� ������",
                                       template:"#day#"
                                      },
                                yAxis:{
                                       title:"���-�� ����������� ������"                                                                        
                                      },
        
			});
			myLineChart_date_zayav.load("get_count_reg_zayav.cgi?SID=$SID", "json");
			
			
			//������� ��������� ������� ������ � ������� ������ � ������� ������� ����������
			myPieChart_debt = new dhtmlXChart({
				view:"pie3D",
				container:"chartbox_debt",
				value:"#summ#",
				
				tooltip:"<b>#summ# %</b>",
				legend:{
					width: 200,					
					align:"right",
					valign:"middle",
					template:"#PAY#"
				},
				gradient:1,
				shadow:true,
				
				color:function(obj){
                               if (obj.PAY == '�� ��������, %') return "#f36ee2";
                               if (obj.PAY == '��������, %') return "#54d2f2";
                               }
			});
			myPieChart_debt.load("get_debts_pays.cgi?SID=$SID", "json");


		}
	</script>

                   <script>
	\$(function(){
	\$('#panel_birthday').panel({
                                      width:352,
                                      height:252,
                                      href:'get_birthdays.cgi?SID=$SID'  
    
                                   }); 
	            });
	</script>
	
	<script> //��������� �������� ��� ��� ������������
    \$(function(){	
       \$.ajax({
            type: 'GET',
            url: 'get_agenda.cgi?SID=$SID',
            cache: false,
            success: function(res1) {   
                                       if (res1.rows.length>0)
                                       {
                                        //alert(res1.rows[0].START_DATE);
                                        \$('#dlg_open_agenda').window('open').dialog('center').dialog('setTitle','�������� ��� �� ������� ���������');
                                        \$('#dg_agenda').datagrid({data: res1});                                     
                                       }
                                     },
            error: function() {alert("did not work");}
            });
                
       })
    </script>   
	
	<script>//������� ��������� ������ �������
    \$(function(){       
       \$('#dg_agenda').datagrid({
	      rowStyler: function(index,row){
		         if (row.KIND_EVENT=="calls"){ return 'background-color:blue;color:#fff;'; }
		         if (row.KIND_EVENT=="linguaterria"){ return 'background-color:#FC5BD5;color:#fff;'; }
		         if (row.KIND_EVENT=="dogovor"){ return 'background-color:red;color:#fff;'; }
		         if (row.KIND_EVENT=="test"){ return 'background-color:orange;color:#fff;'; }
		         if (row.KIND_EVENT=="event"){ return 'background-color:#36BD14;color:#fff;'; }
		         if (row.KIND_EVENT==""){ return 'background-color:#1796b0;color:#fff;'; }
	            }  
            });         
    })
    </script>
	
	 <script>
       \$(function(){  
           var days=$days_expired;
           
           switch (days){
             case 1:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 1 ����. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 2:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 2 ���. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 3:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 3 ���. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 4:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 4 ���. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 5:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 5 ����. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;               
           }      
        })
     </script>
    

        </head>
        <body class="easyui-layout" onload="doOnLoad();">
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
        <!--DIV � ������� ����� ������ ������-->
HTML

       #���������� ������, ������� ����� �� ������� ������
        open FF1, "<txt_data/buttons_panel.txt";
        my @buttons_panel=<FF1>;
        foreach my $str_but (@buttons_panel)
        {
           $str_but=~s/\0//g;
           $str_but=~s/\.\.//g;
           $str_but=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #�� ���� ������ ������� ���� <script>
		   $str_but=~s/SID=\$SID/SID=$SID/i; #����������� ���������� ���� SID � ������ ������ ���������� $SID. ��� �� �� �������������, �.�. ������ �������� �� ���������� �����.
        }
        close (FF1) or die $!;        
        print @buttons_panel;
        #########################################

       print <<HTML1;
        <!--����� DIV � ������� ����� ������ ������-->
        </div>
        <!--����� ������� DIV - ��������� -->

        <!--����� DIV ������ ���� -->
        <div data-options="region:'west',split:false,title:'����'" style="width:205px;">

        <div id='cssmenu'>
        <ul>
HTML1
        #���������� � ��������� ����
        my $us_id=$sess->param('USER_ID'); #������ �� ������ USER_ID
        Build_Menu->menu($us_id, $SID); #� �������� ������� ��������� ID ������������ ��� ������ ����
        
        print <<HTML_e;
        </ul>
        </div>

        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <!-- <div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;"> -->
        <!-- </div> -->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - �������. ������������: $formLogin'">
        
     <!-- ��������� � �� ��������� -->
        <div style="float:left">
          <div id="chartbox" style="width:350px;height:300px;border:1px solid #c0c0c0;">���������� �� �������� ��������</div>
          <div id="panel_birthday" style="border-color:#999; padding-top:10px;"><header style="background-color: #FFFFFF; border-color:#999; color:red;">������� ���� �������� �:</header></div>
        </div>
        <div style="float:left">
          <div id="chartbox_branch" style="width:500px;height:300px;border:1px solid #c0c0c0;">���������� �� ��������</div>
          <div id="chartbox_date_reg" style="width:500px;height:250px;border:1px solid #c0c0c0;">���-�� ����������� ��������� � ������� ������ ( $mon.$year)</div> 
        </div>
        <div style="float:left">
          <div id="chartbox_date_zayav" style="width:500px;height:300px;border:1px solid #c0c0c0;">���-�� �������� ������ � ������� ������ ( $mon.$year)</div>
		  <div id="chartbox_debt" style="width:500px;height:250px;border:1px solid #c0c0c0;">��������� ������� ����� � ������� ������ � ������� ���������� ����</div>
        </div>
		<div>
          <div id="chartdiv" style="width:650px; height:250px; font-size:11px;"></div>
        </div>
        <!-- ����� ��������� � �� ���������-->              

        </div>
        <!-- ����� ����������� DIV -������� ������� -->

        <!-- ����� ��������� ������ -->
        <div id="w" class="easyui-window" title="����� ������" data-options="modal:true,closed:true,iconCls:'icon-save'" style="width:370px;height:170px;padding:10px;">
        <form id="ff" action="javascript:void(null);" onsubmit="call()" method="post" enctype="multipart/form-data">
            <table>
                <tr>
                    <td>������� ������:</td>
                    <td><input id="curr_psw" name="curr_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>����� ������:</td>
                    <td><input name="new_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>��� ���:</td>
                    <td><input name="new_psw1" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td></td>
                    <td><input type="submit" value="�����������"></input></td>
                </tr>
            </table>
        </form>
    </div>
    <!-- ����� ����� ��������� ������ -->
	
	<!-- ����� ������ �������� ��� -->    
    <div id="dlg_open_agenda" class="easyui-dialog" style="width:80%;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg_buttons_agenda" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">             
        <h1 class="shad">�������� ���</h1>                   
        <table id="dg_agenda" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" rownumbers="true" singleSelect="true" fitColumns="true" sortOrder="asc" striped=true>
        <thead>
        <tr>
            <th field="ID" width="10" hidden="true">ID</th>
            <th field="START_DATE" width="30">���� � ����� ������ �������</th>
            <th field="TEXT_MESSAGE" width="70">�������</th>
            <th field="DETAILS" width="60">�����������</th>                                    
            <th field="KIND_EVENT" width="10" hidden="true">ID</th>
        </tr>
        </thead>
        </table>                
    </div> 
    <div id="dlg_buttons_agenda">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="javascript:\$('#dlg_open_agenda').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ������ �������� ��� -->
	
        </body>
        </html>
HTML_e

#���������� ����� ����� ������
$sess->atime(time());
$sess->flush();

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !=~ m/SID=/) {
                        if ($url !=~ m/\?/) {
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