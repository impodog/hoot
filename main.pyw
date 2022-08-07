import traceback
from lib.base import*
from lib.img import*
from lib.module import*
import lib.level as level
__version__="1.5.0"
def main():
    global screen
    loop=True
    room=0
    but_start,but_weapons,but_super,but_controls=pycr.serie_button((100,500),(200,100),"Start","Weapons","Super","Controls",move=(BUTSIZE[0]+50,0),textsize=20)
    text_exit=pycr.text_part((10,650),"Press SHIFT + ESC to exit the game\nPress CTRL + i to show info")
    buts_controls_list=pycr.serie_button((10,200),CONTROL_BUTSIZE,*ALL_CONTROL_SCHEMES,move=(0,CONTROL_BUTSIZE[1]),textsize=30)
    real_damage_emitted=0
    useless_damage_emitted=0
    level.survive_start=time.time()
    OVERLAP=(-30,-15)
    survive_time=0
    kills=0
    refresh=True
    refresh_deadpage=True
    energy_linex=None
    weapons_buts:"list[pycr.button]"=None
    super_buts:"list[pycr.button]"=None
    while loop:
        screen.blit(background,(0,0))
        pycr.PyCr_Value.get_interact()
        for event in pycr.PyCr_Value.event:
            if event.type == pygame.QUIT:loop=False
        level.game_running=room==1
        if room == 0:
            if pycr.put(but_start):room=1
            elif pycr.put(but_weapons):room=2
            elif pycr.put(but_controls):room=3
            elif pycr.put(but_super):room=4
            pycr.put(text_exit)
        elif room == 1:
            if refresh:
                cannon_frar.chpos((100,100))
                level.plyr=player(PLAYER_COLOR,(0,HEALTH_RECT_WIDTH),50,PLAYER_MAX_HEALTH)
                level.player_projlist=list()
                level.enemy_projlist=list()
                level.enemylist=list()
                level.difficulty=START_DIFFICULTY
                level.survive_start=time.time()
                energy_linex=None
                if level.plyr.super is not None:
                    energy_linex=int(SUPERS[level.plyr.super]/PLAYER_MAXENERGY*1000)+1000
                survive_time=0
                real_damage_emitted=0
                useless_damage_emitted=0
                kills=0
                level.start_main_game(math.inf,"Standard")
                level.summon_plane()
                level.summon_aiming_cannon()
                level.summon_skymouse()
                level.summon_mirror()
                refresh=False
            for proj in level.player_projlist:
                pycr.put(proj)
                if not proj.rect.touched(SCREEN_RECT):
                    try:level.player_projlist.remove(proj)
                    except:...
                    proj.death(playerprojlist=level.player_projlist)
                    useless_damage_emitted+=proj.damage
                proj.handle(plyr=level.plyr,playerprojlist=level.player_projlist,enemylist=level.enemylist)
            for proj in level.enemy_projlist:
                pycr.put(proj)
                if not proj.rect.touched(SCREEN_RECT):
                    try:level.enemy_projlist.remove(proj)
                    except:...
                if level.plyr.rect.touched(proj.rect):
                    if not proj.undestroyable:
                        try:level.enemy_projlist.remove(proj)
                        except:...
                        proj.death()
                    level.plyr.health-=proj.damage
                proj.handle(enemyprojlist=level.enemy_projlist)
            for ene in level.enemylist:
                if level.plyr.rect.touched(ene.rect):
                    level.plyr.health-=0.3
                    ene.health-=0.1
                for proj in level.player_projlist:
                    if proj.rect.touched(ene.rect):
                        if ene.collide(proj):
                            emit=min(proj.damage,ene.health)
                            if not proj.undestroyable:
                                try:level.player_projlist.remove(proj)
                                except:...
                                proj.death(playerprojlist=level.player_projlist)
                            if not isinstance(proj,player_super_proj):level.plyr.energy+=emit/2
                            real_damage_emitted+=emit
                            useless_damage_emitted+=proj.damage-emit
                            ene.health-=proj.damage
                for proj in level.enemy_projlist:
                    if isinstance(proj,boom):
                        if proj.rect.touched(ene.rect):
                            ene.health-=proj.damage
                if ene.health <= 0 or (not ene.rect.touched(SCREEN_RECT)):
                    ene.death(enemyprojlist=level.enemy_projlist,plyr=level.plyr)
                    if ene.health <= 0:kills+=1
                    try:level.enemylist.remove(ene)
                    except:...
                enemyshoot=ene.shoot(plyr_pos=level.plyr.rect.center)
                if enemyshoot is not None:
                    level.enemy_projlist.extend(enemyshoot)
                pycr.put(ene)
                ene.handle(enemyprojlist=level.enemy_projlist,enemylist=level.enemylist,plyr=level.plyr,playerprojlist=level.player_projlist)
            pycr.put(level.plyr)
            player_shoot=level.plyr.shoot()
            if player_shoot is not None:
                level.player_projlist.extend(player_shoot)
            player_super=level.plyr.super_use(level.enemylist,level.player_projlist)
            if player_super is not None:
                level.player_projlist.extend(player_super)
            if level.plyr.health <= 0:room=-1;survive_time=time.time()-level.survive_start
            pycr.put(pycr.text_part((10,1000),"Weapon %s\n\nTime %.2f"%(level.plyr.weapon,time.time()-level.survive_start)))
            pygame.draw.rect(screen,RED,(0,0,1000,HEALTH_RECT_WIDTH))
            pygame.draw.rect(screen,GREEN,(0,0,int(level.plyr.health/PLAYER_MAX_HEALTH*1000),HEALTH_RECT_WIDTH))
            pygame.draw.rect(screen,YELLOW,(1000,0,1000,HEALTH_RECT_WIDTH))
            pygame.draw.rect(screen,BLUE,(1000,0,int(level.plyr.energy/PLAYER_MAXENERGY*1000),HEALTH_RECT_WIDTH))
            if energy_linex is not None:pygame.draw.line(screen,BLACK,(energy_linex,0),(energy_linex,HEALTH_RECT_WIDTH),2)
            pycr.put(pycr.text_part((0,0),"Health %d/%d"%(level.plyr.health,PLAYER_MAX_HEALTH),HEALTH_RECT_WIDTH))
            pycr.put(pycr.text_part((1000,0),"Energy %d/%d"%(level.plyr.energy,PLAYER_MAXENERGY),HEALTH_RECT_WIDTH,WHITE if level.plyr.energy > 10 else BLACK))
        elif room == 2:
            if weapons_buts is None:
                weapons_buts=[pycr.text_part((10,1050),"Left:Chosen  Right:Not Chosen\nClick to swap weapon chosen/not chosen\nESC to quit")]
                chosen=igvar_()["weapons-chosen"]
                cury=0
                for i in chosen:
                    weapons_buts.append(pycr.button((0,cury),pycr.overlap2((0,cury),BUTSIZE),(i,i)))
                    cury+=BUTSIZE[1]
                not_chosen=WEAPONS.copy()
                for i in chosen:not_chosen.remove(i)
                cury=0
                for i in not_chosen:
                    weapons_buts.append(pycr.button((BUTSIZE[0],cury),pycr.overlap2((BUTSIZE[0],cury),BUTSIZE),(i,i)))
                    cury+=BUTSIZE[1]
            result = pycr.puts(*weapons_buts)
            clicked:pycr.button=None
            for res in result:
                if res[1] is True:clicked=res[0];break
            if clicked is not None:
                wp=clicked.text[0]
                if wp in chosen:
                    if len(chosen) > 1:
                        igvar_()["weapons-chosen"].remove(wp)
                else:
                    igvar_()["weapons-chosen"].append(wp)
                weapons_buts=None
        elif room == 3:
            result=pycr.puts(*buts_controls_list)
            for but,ret in result:
                if ret is True:
                    igvar_()["key-scheme"]=but.text[0]
            pycr.put(pycr.text_part((10,10),"Scheme : %s\nESC to quit"%igvar_()["key-scheme"],40))
        elif room == 4:
            if super_buts is None:
                super_buts=[pycr.text_part((10,1000),"Left:Chosen  Right:Not Chosen\nChoose one of the supers on the right to use it\nESC to quit")]
                chosen=igvar_()["super-chosen"]
                not_chosen=list(SUPERS.keys())
                if chosen is not None:
                    super_buts.append(pycr.button((0,0),BUTSIZE,(chosen,chosen)))
                    not_chosen.remove(chosen)
                cury=0
                for i in not_chosen:
                    super_buts.append(pycr.button((BUTSIZE[0],cury),pycr.overlap2((BUTSIZE[0],cury),BUTSIZE),(i,i)))
                    cury+=BUTSIZE[1]
            result = pycr.puts(*super_buts)
            clicked:pycr.button=None
            for res in result:
                if res[1] is True:clicked=res[0];break
            if clicked is not None:
                sp=clicked.text[0]
                if sp != chosen:
                    igvar_()["super-chosen"]=sp
                super_buts=None
        elif room == -1:
            if refresh_deadpage:
                weapons_used=len(igvar_()["weapons-chosen"])
                score=(real_damage_emitted-useless_damage_emitted+kills*5)*survive_time**1.1/10/math.sqrt(weapons_used)
                if igvar_()["best-time"] > survive_time:time_record="Best Time %.2f s"%igvar_()["best-time"]
                else:
                    time_record="New Best Time"
                    igvar_()["best-time"]=survive_time
                text="""RESULTS

Real Damage Emitted    : %.2f hp    Damage that hurt enemies
Useless Damage Emitted : %.2f hp    Damage that did not touch any enemies or overflowed (the enemy didn't have enough health to take all of the damage)

Enemies Killed : %d
Time Survived  : %.2f s

Weapons Used   : %d

Score : %.2f

%s

Press ESC to exit here"""%(real_damage_emitted,useless_damage_emitted,kills,survive_time,weapons_used,score,time_record)

                dead_tp=pycr.text_part((100,100),text,25)
            pycr.put(dead_tp)
        if pycr.PyCr_Value.key == pygame.K_ESCAPE:
            room=0
            refresh=True
            refresh_deadpage=True
            weapons_buts=None
            if pycr.PyCr_Value.mod & pygame.KMOD_SHIFT:loop=False
        if pycr.PyCr_Value.mod & pygame.KMOD_CTRL:
            if pycr.PyCr_Value.key == pygame.K_i:
                pyautogui.alert("Version : %s"%__version__,"Hoot Info")
        pygame.display.flip()
        pycr.clock.tick(50)
if __name__ == "__main__":
    try:main()
    except:traceback.print_exc()
    save_igvar()
    level.game_running=False
