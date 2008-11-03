package Dough::CGI;

use CGI qw/:all/;
use JSON::XS;

use Dough::Config;
use Dough::Log;
use Dough::CGI::Process;

sub new {
	my $class = shift;
	my $self = {};

	bless($self, $class);
	$self->{q} = new CGI;
	$self->{resp} = {};
	$self->{l} = Dough::Log->instance();

	return $self;
}

sub processQuery {
	my $s = shift;

	my $q = $s->{q};
	my $rm = $q->request_method();
	my $phid = $s->{phid} = $q->param('phid');
	my $act = $s->{act} = $q->param('act');

	my $procFunc = \&Dough::CGI::Process::queryWithAttributes;

	if ($phid) {
		if ($rm eq "POST") {
		}
		else {
			if ($act eq 'qwa') {
				$procFunc = \&process_QueryWithAttribute;
			}
		}
	}
	else {
		$s->{resp} = { 'Error' => 'No Device ID given; not enough arguments.' };
	}

	if (defined($procFunc)) {
		$s->{resp} = &$procFunc($s);
		print "PROC FUNC result: $s->{resp}\n";
	}
	else {
		$s->{l}->log("Undefined procFunc!");
	}
}

sub sendResponse {
	my $s = shift;

	print $s->{q}->header();
	print encode_json($s->{resp});
}
1;
