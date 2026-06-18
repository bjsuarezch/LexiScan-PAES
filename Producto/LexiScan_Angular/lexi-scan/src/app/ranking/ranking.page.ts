import { Component, OnInit } from '@angular/core';
import { ProfileService } from '../services/profile.service';
import { RankingUserItem } from '../models/backend.model';
import { NavController } from '@ionic/angular';

@Component({
  selector: 'app-ranking',
  templateUrl: './ranking.page.html',
  styleUrls: ['./ranking.page.scss'],
  standalone: false
})
export class RankingPage implements OnInit {
  ranking: RankingUserItem[] = [];
  usuarioActual: RankingUserItem | null = null;
  loading = true;

  constructor(
    private profileService: ProfileService,
    private navCtrl: NavController
  ) { }

  ngOnInit() {
    this.loadRanking();
  }

  loadRanking() {
    this.profileService.getProfile().subscribe(profile => {
      const rut = profile?.rut || undefined;
      this.profileService.getRanking(rut, 10).subscribe({
        next: (res) => {
          this.ranking = res.ranking;
          this.usuarioActual = res.usuario_actual || null;
          this.loading = false;
        },
        error: (err) => {
          console.error('Error al cargar el ranking:', err);
          this.loading = false;
        }
      });
    });
  }

  goBack() {
    this.navCtrl.back();
  }
}
