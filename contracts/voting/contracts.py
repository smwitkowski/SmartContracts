from pyteal import *


def approval_program():

    akita_id = 384303832

    # Define the registration and voting periods
    on_creation = Seq([
        App.globalPut(Bytes('Creator'), Txn.sender(),),
        Assert(Txn.application_args.length() == Int(4)),
        App.globalPut(Bytes('RegistrationStart'),
                      Btoi(Txn.application_args[0])),
        App.globalPut(Bytes('RegistrationEnd'),
                      Btoi(Txn.application_args[1])),
        App.globalPut(Bytes('VotingStart'),
                      Btoi(Txn.application_args[2])),
        App.globalPut(Bytes('VotingEnd'),
                      Btoi(Txn.application_args[3])),
        # TODO define valid choices and assert in on_vote
        #App.globalPut(Bytes('VotingChoices'),)
        Return(Int(1))
    ])

    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes('voted'))
    is_creator = Txn.sender() == App.globalGet(Bytes('Creator'))

    # Define the op-out program
    on_closeout = Seq([
        get_vote_of_sender,
        If(
            # If a user opts out before the end of voting and has voted
            And(
                Global.round() <= App.globalGet(Bytes('VotingEnd')),
                get_vote_of_sender.hasValue()),
            # Remove 1 tally from the voter's choice
            App.globalPut(get_vote_of_sender.value(),
                          App.globalGet(get_vote_of_sender.value()) - Int(1))),
        Return(Int(1))
    ])

    on_register = Seq([
        # Assert the sender is registering in the appropriate period
        Return(And(
            Global.round() >= App.globalGet(Bytes("RegistrationStart")),
            Global.round() <= App.globalGet(Bytes("RegistrationEnd")),
            AssetHolding.balance(Txn.sender(), akita_id).value() > 0
        ))
    ])

    choice = Txn.application_args[1]
    choice_tally = App.globalGet(choice)

    # Define voting process
    on_vote = Seq([
        Assert(And(
            # Assert vote was cast within voting period
            Global.round() >= App.globalGet(Bytes("VotingStart")),
            Global.round() <= App.globalGet(Bytes("VotingEnd")),
            # Assert that voter holds Akita
            AssetHolding.balance(Txn.sender(), akita_id).value() > 0
        )),
        # Get the voter's choice proceed if they have not already voted
        get_vote_of_sender,
        If(get_vote_of_sender.hasValue(), Return(Int(0))),
        # Add one to the vote tally
        App.globalPut(choice, choice_tally + Int(1)),
        # Record the voter's choice to their local state
        App.localPut(Int(0), Bytes('voted'), choice),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, on_register],
        [Txn.application_args[0] == Bytes("vote"), on_vote]
    )

    return program


def clear_state_program():
    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes("voted"))
    program = Seq([
        get_vote_of_sender,
        If(And(Global.round() <= App.globalGet(Bytes("VoteEnd")), get_vote_of_sender.hasValue()),
            App.globalPut(get_vote_of_sender.value(), App.globalGet(get_vote_of_sender.value()) - Int(1))
        ),
        Return(Int(1))
    ])

    return program


def compile():
    with open('vote_approval.teal', 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)

    with open('vote_clear_state.teal', 'w') as f:
        compiled = compileTeal(clear_state_program(), Mode.Application)
        f.write(compiled)