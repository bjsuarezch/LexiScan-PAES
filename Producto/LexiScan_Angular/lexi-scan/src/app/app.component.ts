import { Component, OnInit, OnDestroy } from '@angular/core';
import { HabilidadesService } from './services/habilidades.service';
import { Subscription, interval } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styleUrls: ['app.component.scss'],
  standalone: false,
})
export class AppComponent implements OnInit, OnDestroy {
  backendIsDown = false;
  private healthSub: Subscription | null = null;

  constructor(private habilidadesService: HabilidadesService) {}

  ngOnInit() {
    this.checkHealth();
    // Poll health every 15 seconds
    this.healthSub = interval(15000).subscribe(() => {
      this.checkHealth();
    });
  }

  ngOnDestroy() {
    if (this.healthSub) {
      this.healthSub.unsubscribe();
    }
  }

  private checkHealth() {
    this.habilidadesService.checkBackendHealth().subscribe({
      next: () => this.backendIsDown = false,
      error: () => this.backendIsDown = true
    });
  }
}
