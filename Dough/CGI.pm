package Dough::CGI;

use CGI qw/:all/;
use JSON::XS;

use Dough::Config;
use Dough::Log;
use Dough::CGI::Process;
use Dough::SDB;

sub new {
	my $class = shift;
	my $self = {};

	bless($self, $class);
	$self->{q} = new CGI;
	$self->{resp} = {};
	$self->{l} = Dough::Log->instance();
    $self->{sdb} = Dough::SDB->new();

	return $self;
}

sub processQuery {
	my $s = shift;

	my $q = $s->{q};
	my $rm = $q->request_method();
	my $phid = $s->{phid} = $q->param('phid');
	my $act = $s->{act} = $q->param('act');

    my $procFunc;

	if ($phid) {
		if ($rm eq "POST") {
		}
		else {
			if ($act eq 'qwa') {
	            $procFunc = \&Dough::CGI::Process::qwa;
			}
		}
	}
	else {
		$s->{resp} = { 'Error' => 'No Device ID given; not enough arguments.' };
	}

	if (defined($procFunc)) {
		$s->{resp} = &$procFunc($s);
		$s->{l}->log("PROC FUNC result: $s->{resp}");
	}
	else {
		$s->{l}->log("Undefined procFunc!");
	}

    return $s->{resp};
}

sub sendResponse {
	my $s = shift;

	print $s->{q}->header();
	print encode_json($s->{resp});
}
1;
