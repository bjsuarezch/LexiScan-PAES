import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IonicModule } from '@ionic/angular';

import { ExamenPage } from './examen.page';

describe('ExamenPage', () => {
  let component: ExamenPage;
  let fixture: ComponentFixture<ExamenPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExamenPage ],
      imports: [IonicModule.forRoot()]
    }).compileComponents();

    fixture = TestBed.createComponent(ExamenPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
