import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from .models import Draw, Ticket, WinResult
from .forms import RegisterForm, ManualTicketForm


def is_admin(user):
    return user.is_staff


# ───────────── 공통 ─────────────

def home(request):
    latest_draw = Draw.objects.filter(is_completed=True).first()
    return render(request, 'lotto/home.html', {'latest_draw': latest_draw})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'lotto/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'lotto/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ───────────── 일반 사용자 ─────────────

@login_required
def buy_ticket(request):
    draws = Draw.objects.filter(is_completed=False)
    if not draws.exists():
        messages.warning(request, '현재 구매 가능한 회차가 없습니다.')
        return render(request, 'lotto/buy.html', {'form': None, 'draws': []})

    latest_draw = draws.first()
    form = ManualTicketForm()

    if request.method == 'POST':
        mode = request.POST.get('mode', 'manual')

        if mode == 'auto':
            nums = random.sample(range(1, 46), 6)
            numbers_str = ','.join(str(n) for n in sorted(nums))
            Ticket.objects.create(
                user=request.user,
                draw=latest_draw,
                numbers=numbers_str,
                mode='auto'
            )
            messages.success(request, f'자동 번호 [{numbers_str}] 구매 완료!')
            return redirect('my_tickets')

        else:
            form = ManualTicketForm(request.POST)
            if form.is_valid():
                Ticket.objects.create(
                    user=request.user,
                    draw=latest_draw,
                    numbers=form.cleaned_data['numbers'],
                    mode='manual'
                )
                messages.success(request, '수동 번호 구매 완료!')
                return redirect('my_tickets')

    return render(request, 'lotto/buy.html', {
        'form': form,
        'draw': latest_draw,
    })


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('draw').order_by('-purchased_at')
    return render(request, 'lotto/my_tickets.html', {'tickets': tickets})


@login_required
def check_win(request):
    results = WinResult.objects.filter(user=request.user).select_related('draw', 'ticket').order_by('-confirmed_at')
    return render(request, 'lotto/check_win.html', {'results': results})


# ───────────── 관리자 ─────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_tickets = Ticket.objects.count()
    total_draws = Draw.objects.filter(is_completed=True).count()
    latest_draw = Draw.objects.filter(is_completed=True).first()
    return render(request, 'lotto/admin_dashboard.html', {
        'total_tickets': total_tickets,
        'total_draws': total_draws,
        'latest_draw': latest_draw,
    })


@login_required
@user_passes_test(is_admin)
def admin_draw(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            last = Draw.objects.first()
            new_round = (last.round + 1) if last else 1
            Draw.objects.create(round=new_round)
            messages.success(request, f'{new_round}회차가 생성되었습니다.')

        elif action == 'draw':
            draw_id = request.POST.get('draw_id')
            draw = Draw.objects.get(id=draw_id)
            if not draw.is_completed:
                nums = sorted(random.sample(range(1, 46), 6))
                bonus = random.choice([n for n in range(1, 46) if n not in nums])
                draw.numbers = ','.join(str(n) for n in nums)
                draw.bonus = bonus
                draw.drawn_at = timezone.now()
                draw.is_completed = True
                draw.save()
                _calculate_results(draw)
                messages.success(request, f'{draw.round}회차 추첨 완료! 당첨번호: {draw.numbers} | 보너스: {bonus}')
            else:
                messages.warning(request, '이미 추첨된 회차입니다.')

        return redirect('admin_draw')

    draws = Draw.objects.all()
    return render(request, 'lotto/admin_draw.html', {'draws': draws})


def _calculate_results(draw):
    win_nums = set(draw.get_numbers_list())
    bonus = draw.bonus
    tickets = Ticket.objects.filter(draw=draw)

    for ticket in tickets:
        t_nums = set(ticket.get_numbers_list())
        match = len(win_nums & t_nums)
        bonus_match = bonus in t_nums

        if match == 6:
            rank = 1
        elif match == 5 and bonus_match:
            rank = 2
        elif match == 5:
            rank = 3
        elif match == 4:
            rank = 4
        elif match == 3:
            rank = 5
        else:
            rank = 0

        WinResult.objects.create(
            draw=draw,
            user=ticket.user,
            ticket=ticket,
            rank=rank,
        )


@login_required
@user_passes_test(is_admin)
def admin_sales(request):
    tickets = Ticket.objects.select_related('user', 'draw').order_by('-purchased_at')
    return render(request, 'lotto/admin_sales.html', {'tickets': tickets})


@login_required
@user_passes_test(is_admin)
def admin_results(request):
    results = WinResult.objects.select_related('user', 'draw', 'ticket').order_by('-confirmed_at')
    return render(request, 'lotto/admin_results.html', {'results': results})
