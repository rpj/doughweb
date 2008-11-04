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

    if (!(scalar($self->{q}->param))) {
        return undef;
    }

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
		if ($rm eq "GET") {
            if ($act eq 'ta') {
                $s->{sha} = $q->param('sha');
                $s->{json} = decode_json($q->param('json')), if ($q->param('json'));

                $procFunc = \&Dough::CGI::Process::ta, if ($s->{sha} && $s->{json});
            }
		}
		else {
			if ($act eq 'qwa') {
	            $procFunc = \&Dough::CGI::Process::qwa;
			}
		}
	}
	else {
		$s->{resp} = { 'Error' => 'Insufficient arguments.' };
	}

	if (defined($procFunc)) {
		$s->{resp} = &$procFunc($s);
        $s->{l}->log("No result from $procFunc!"), unless(defined($s->{resp}));
	}

    return $s->{resp};
}

sub sendResponseAsJSON {
	my $s = shift;

	#print $s->{q}->header('application/json');
    print $s->{q}->header('text/plain');
	print encode_json($s->{resp});

    return !(defined($s->{resp}->{Error}));
}
1;
