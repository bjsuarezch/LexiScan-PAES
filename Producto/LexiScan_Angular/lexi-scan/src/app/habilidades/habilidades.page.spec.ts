import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { HabilidadesPage } from './habilidades.page';

describe('HabilidadesPage', () => {
  let component: HabilidadesPage;
  let fixture: ComponentFixture<HabilidadesPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HabilidadesPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(HabilidadesPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
